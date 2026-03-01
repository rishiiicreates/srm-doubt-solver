"""
PPT Scraper & Downloader for thehelpers.vercel.app.

Crawls the site to discover all semester/subject/resource links,
extracts Google Drive file/folder IDs, and downloads PPT files
into data/{semester}/{subject}/ directories.

Produces a manifest.json that maps every discovered resource.
"""

import hashlib
import json
import os
import re
import time
import urllib.parse
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

try:
    import gdown
except ImportError:
    gdown = None  # graceful degradation

from config import (
    DATA_DIR,
    HELPERS_BASE_URL,
    HELPERS_SEMESTERS_URL,
    MANIFEST_PATH,
    TOTAL_SEMESTERS,
    REQUEST_DELAY_SECONDS,
    MAX_RETRIES,
)


# ── Data Classes ──────────────────────────────────────────────────────────────


@dataclass
class Resource:
    """A single downloadable resource discovered on the site."""
    name: str
    resource_type: str  # "unit_notes", "pyq", "syllabus", "other"
    semester: int
    subject: str
    drive_url: Optional[str] = None
    drive_id: Optional[str] = None
    drive_type: Optional[str] = None  # "file" or "folder"
    local_path: Optional[str] = None
    downloaded: bool = False
    md5_hash: Optional[str] = None
    source_page_url: Optional[str] = None


@dataclass
class SubjectInfo:
    """A subject within a semester."""
    name: str
    semester: int
    url: str
    resources: list = field(default_factory=list)


@dataclass
class Manifest:
    """Full manifest of all discovered resources."""
    scraped_at: str = ""
    total_semesters_scraped: int = 0
    total_subjects: int = 0
    total_resources: int = 0
    total_downloaded: int = 0
    subjects: list = field(default_factory=list)


# ── Helper Functions ──────────────────────────────────────────────────────────


def _md5(filepath: str) -> str:
    """Compute MD5 hash of a file."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_dirname(name: str) -> str:
    """Convert a subject name to a filesystem-safe directory name."""
    safe = re.sub(r"[^\w\s-]", "", name.strip())
    safe = re.sub(r"\s+", "_", safe)
    return safe.lower()


def _extract_drive_id(url: str) -> tuple[Optional[str], Optional[str]]:
    """
    Extract Google Drive file/folder ID from a URL.
    Returns (drive_id, drive_type) where drive_type is 'file' or 'folder'.
    """
    if not url:
        return None, None

    # Folder pattern: /drive/folders/{ID}
    folder_match = re.search(r"/folders/([a-zA-Z0-9_-]+)", url)
    if folder_match:
        return folder_match.group(1), "folder"

    # File pattern: /file/d/{ID}
    file_match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if file_match:
        return file_match.group(1), "file"

    # Open pattern: ?id={ID}
    id_match = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
    if id_match:
        return id_match.group(1), "file"

    return None, None


def _fetch(url: str, retries: int = MAX_RETRIES, delay: float = REQUEST_DELAY_SECONDS) -> Optional[str]:
    """Fetch a URL with retries and polite delay."""
    for attempt in range(retries):
        try:
            time.sleep(delay)
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            wait = (2 ** attempt) * delay
            print(f"  ⚠ Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            if attempt < retries - 1:
                print(f"    Retrying in {wait:.1f}s...")
                time.sleep(wait)
    return None


# ── Scraping Logic ────────────────────────────────────────────────────────────


def scrape_subjects_for_semester(semester: int) -> list[SubjectInfo]:
    """Scrape all subject names and URLs for a given semester."""
    url = f"{HELPERS_SEMESTERS_URL}/{semester}"
    print(f"\n📚 Scraping Semester {semester}: {url}")

    html = _fetch(url)
    if not html:
        print(f"  ❌ Failed to fetch semester {semester} page")
        return []

    soup = BeautifulSoup(html, "lxml")
    subjects = []

    # Look for subject links — these are <a> tags pointing to /semesters/{n}/subjects/{name}
    pattern = re.compile(rf"/semesters/{semester}/subjects/")
    for link in soup.find_all("a", href=pattern):
        href = link.get("href", "")
        # Extract subject name from the link text or from URL
        name = link.get_text(strip=True)
        if not name:
            # Decode from URL
            parts = href.split("/subjects/")
            if len(parts) > 1:
                name = urllib.parse.unquote(parts[1]).strip("/")

        if name:
            full_url = urllib.parse.urljoin(HELPERS_BASE_URL, href)
            subjects.append(SubjectInfo(name=name, semester=semester, url=full_url))
            print(f"  📖 Found subject: {name}")

    # Fallback: look for any clickable cards/buttons with subject-like text
    if not subjects:
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if f"/semesters/{semester}/" in href and "/subjects/" in href:
                name = link.get_text(strip=True)
                if name:
                    full_url = urllib.parse.urljoin(HELPERS_BASE_URL, href)
                    subjects.append(SubjectInfo(name=name, semester=semester, url=full_url))
                    print(f"  📖 Found subject (fallback): {name}")

    if not subjects:
        print(f"  ℹ No subjects found for semester {semester}")

    return subjects


def scrape_resources_for_subject(subject: SubjectInfo) -> list[Resource]:
    """Scrape all resource links for a given subject."""
    print(f"\n  🔍 Scraping resources for: {subject.name} (Semester {subject.semester})")

    html = _fetch(subject.url)
    if not html:
        print(f"    ❌ Failed to fetch subject page: {subject.url}")
        return []

    soup = BeautifulSoup(html, "lxml")
    resources = []

    # Strategy 1: Look for links to Google Drive (direct in page or in data attributes)
    drive_pattern = re.compile(r"drive\.google\.com")
    for link in soup.find_all("a", href=drive_pattern):
        href = link.get("href", "")
        name = link.get_text(strip=True) or "Resource"
        drive_id, drive_type = _extract_drive_id(href)

        res = Resource(
            name=name,
            resource_type=_classify_resource(name),
            semester=subject.semester,
            subject=subject.name,
            drive_url=href,
            drive_id=drive_id,
            drive_type=drive_type,
            source_page_url=subject.url,
        )
        resources.append(res)
        print(f"    📎 Found Drive link: {name} ({drive_type}: {drive_id})")

    # Strategy 2: Look for links to internal viewer pages
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if "folder-viewer" in href or "file-viewer" in href or "secure-viewer" in href:
            # Try to extract the Google Drive URL from query params
            parsed = urllib.parse.urlparse(urllib.parse.urljoin(HELPERS_BASE_URL, href))
            params = urllib.parse.parse_qs(parsed.query)

            drive_url = params.get("url", [None])[0]
            if drive_url:
                drive_url = urllib.parse.unquote(drive_url)
                drive_id, drive_type = _extract_drive_id(drive_url)
            else:
                drive_id, drive_type = None, None
                drive_url = None

            name = link.get_text(strip=True) or "Resource"

            res = Resource(
                name=name,
                resource_type=_classify_resource(name),
                semester=subject.semester,
                subject=subject.name,
                drive_url=drive_url,
                drive_id=drive_id,
                drive_type=drive_type,
                source_page_url=subject.url,
            )
            resources.append(res)
            print(f"    📎 Found viewer link: {name} (drive_id: {drive_id})")

    # Strategy 3: Look for iframes with Google Drive embeds
    for iframe in soup.find_all("iframe", src=True):
        src = iframe.get("src", "")
        if "drive.google.com" in src:
            drive_id, drive_type = _extract_drive_id(src)
            res = Resource(
                name=f"Embedded {drive_type or 'resource'}",
                resource_type="other",
                semester=subject.semester,
                subject=subject.name,
                drive_url=src,
                drive_id=drive_id,
                drive_type=drive_type,
                source_page_url=subject.url,
            )
            resources.append(res)
            print(f"    📎 Found iframe embed: {drive_id}")

    # Strategy 4: Parse script tags / Next.js data for embedded Drive URLs
    for script in soup.find_all("script"):
        text = script.string or ""
        # Find all Google Drive URLs in script content
        drive_urls = re.findall(
            r'https?://drive\.google\.com/[^\s"\'<>]+', text
        )
        for durl in drive_urls:
            drive_id, drive_type = _extract_drive_id(durl)
            if drive_id and not any(r.drive_id == drive_id for r in resources):
                res = Resource(
                    name=f"Script-embedded {drive_type or 'resource'}",
                    resource_type="other",
                    semester=subject.semester,
                    subject=subject.name,
                    drive_url=durl,
                    drive_id=drive_id,
                    drive_type=drive_type,
                    source_page_url=subject.url,
                )
                resources.append(res)
                print(f"    📎 Found in script data: {drive_id}")

    if not resources:
        print(f"    ℹ No downloadable resources found for {subject.name}")

    return resources


def _classify_resource(name: str) -> str:
    """Classify a resource type from its name."""
    name_lower = name.lower()
    if any(kw in name_lower for kw in ["unit", "notes", "module", "chapter"]):
        return "unit_notes"
    if any(kw in name_lower for kw in ["pyq", "previous", "question", "ct", "exam"]):
        return "pyq"
    if any(kw in name_lower for kw in ["syllabus"]):
        return "syllabus"
    return "other"


# ── Download Logic ────────────────────────────────────────────────────────────


def download_resource(resource: Resource) -> bool:
    """Download a single resource from Google Drive."""
    if not resource.drive_id:
        print(f"    ⏭ No drive ID for: {resource.name}")
        return False

    # Create target directory
    sem_dir = f"semester_{resource.semester}"
    subj_dir = _safe_dirname(resource.subject)
    target_dir = os.path.join(DATA_DIR, sem_dir, subj_dir)
    os.makedirs(target_dir, exist_ok=True)

    safe_name = _safe_dirname(resource.name)
    if not safe_name:
        safe_name = resource.drive_id

    if resource.drive_type == "folder":
        # For folders, we download all files in the folder
        return _download_drive_folder(resource.drive_id, target_dir, resource)
    else:
        # For individual files
        return _download_drive_file(resource.drive_id, target_dir, safe_name, resource)


def _download_drive_file(drive_id: str, target_dir: str, name: str, resource: Resource) -> bool:
    """Download a single file from Google Drive."""
    if gdown is None:
        print(f"    ⚠ gdown not installed. Cannot download {name}.")
        print(f"      Install with: pip install gdown")
        return False

    url = f"https://drive.google.com/uc?id={drive_id}"

    # Determine output path
    output_path = os.path.join(target_dir, f"{name}")
    # gdown will add extension if needed

    try:
        print(f"    ⬇ Downloading: {name} -> {target_dir}/")
        result = gdown.download(url, output=output_path, quiet=False, fuzzy=True)
        if result and os.path.exists(result):
            resource.local_path = result
            resource.downloaded = True
            resource.md5_hash = _md5(result)
            print(f"    ✅ Downloaded: {os.path.basename(result)} (MD5: {resource.md5_hash[:8]}...)")
            return True
        else:
            print(f"    ❌ Download failed for: {name}")
            return False
    except Exception as e:
        print(f"    ❌ Download error for {name}: {e}")
        return False


def _download_drive_folder(drive_id: str, target_dir: str, resource: Resource) -> bool:
    """Download all files from a Google Drive folder."""
    if gdown is None:
        print(f"    ⚠ gdown not installed. Cannot download folder.")
        return False

    url = f"https://drive.google.com/drive/folders/{drive_id}"

    try:
        print(f"    ⬇ Downloading folder: {resource.name} -> {target_dir}/")
        files = gdown.download_folder(url, output=target_dir, quiet=False)
        if files:
            resource.downloaded = True
            resource.local_path = target_dir
            downloaded_files = [f for f in os.listdir(target_dir)
                                if os.path.isfile(os.path.join(target_dir, f))]
            print(f"    ✅ Downloaded {len(downloaded_files)} files from folder")
            return True
        else:
            print(f"    ❌ Folder download failed or empty")
            return False
    except Exception as e:
        print(f"    ❌ Folder download error: {e}")
        return False


# ── Main Scraper Pipeline ────────────────────────────────────────────────────


def scrape_and_download(download: bool = True) -> Manifest:
    """
    Full scraping pipeline:
    1. Discover all subjects across all semesters
    2. Discover all resources for each subject
    3. Optionally download all discovered resources
    4. Save manifest.json

    Args:
        download: If True, attempt to download discovered resources.

    Returns:
        Manifest with all discovered resources.
    """
    print("=" * 60)
    print("🌐 SRM Syllabus Scraper — thehelpers.vercel.app")
    print("=" * 60)

    manifest = Manifest()
    manifest.scraped_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    all_subjects = []

    # Phase 1: Discover subjects for each semester
    for sem in range(1, TOTAL_SEMESTERS + 1):
        subjects = scrape_subjects_for_semester(sem)
        all_subjects.extend(subjects)

    manifest.total_semesters_scraped = TOTAL_SEMESTERS
    manifest.total_subjects = len(all_subjects)

    # Phase 2: Discover resources for each subject
    for subject in all_subjects:
        resources = scrape_resources_for_subject(subject)
        subject.resources = resources
        manifest.total_resources += len(resources)

    # Phase 3: Download resources
    if download:
        print("\n" + "=" * 60)
        print("⬇ Downloading resources...")
        print("=" * 60)

        for subject in all_subjects:
            for resource in subject.resources:
                success = download_resource(resource)
                if success:
                    manifest.total_downloaded += 1

    # Phase 4: Save manifest
    manifest.subjects = [
        {
            "name": s.name,
            "semester": s.semester,
            "url": s.url,
            "resources": [asdict(r) for r in s.resources],
        }
        for s in all_subjects
    ]

    save_manifest(manifest)

    # Summary
    print("\n" + "=" * 60)
    print("📊 Scraping Summary")
    print("=" * 60)
    print(f"  Semesters scraped:  {manifest.total_semesters_scraped}")
    print(f"  Subjects found:    {manifest.total_subjects}")
    print(f"  Resources found:   {manifest.total_resources}")
    print(f"  Files downloaded:  {manifest.total_downloaded}")
    print(f"  Manifest saved to: {MANIFEST_PATH}")

    return manifest


def save_manifest(manifest: Manifest) -> None:
    """Save manifest to JSON file."""
    data = {
        "scraped_at": manifest.scraped_at,
        "total_semesters_scraped": manifest.total_semesters_scraped,
        "total_subjects": manifest.total_subjects,
        "total_resources": manifest.total_resources,
        "total_downloaded": manifest.total_downloaded,
        "subjects": manifest.subjects,
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_manifest() -> Optional[dict]:
    """Load existing manifest if it exists."""
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def get_file_hashes_from_manifest() -> dict[str, str]:
    """Return a dict of {filepath: md5_hash} from the manifest."""
    manifest = load_manifest()
    if not manifest:
        return {}

    hashes = {}
    for subject in manifest.get("subjects", []):
        for resource in subject.get("resources", []):
            if resource.get("local_path") and resource.get("md5_hash"):
                hashes[resource["local_path"]] = resource["md5_hash"]
    return hashes


if __name__ == "__main__":
    scrape_and_download(download=True)
