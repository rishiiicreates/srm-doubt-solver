"""
Metadata Extractor — tags each document chunk with structured metadata
extracted from file paths, filenames, and slide content.

Metadata fields:
  - semester (int): Semester number from directory path
  - subject (str): Subject name from directory structure
  - unit_number (int): Unit number from filename or content
  - slide_number (int): Slide/page number in the original file
  - source_filename (str): Original filename
  - source_url (str): URL from the manifest (if available)
"""

import os
import re
from typing import Optional


def extract_metadata_from_path(filepath: str) -> dict:
    """
    Extract metadata from a file's path in the data/{semester}/{subject}/ structure.

    Example path: data/semester_3/data_structures/unit2_slides.pptx
    Extracts: semester=3, subject="data_structures", source_filename="unit2_slides.pptx"
    """
    filepath = os.path.normpath(filepath)
    parts = filepath.split(os.sep)

    metadata = {
        "semester": 0,
        "subject": "unknown",
        "unit_number": 0,
        "slide_number": 0,
        "source_filename": os.path.basename(filepath),
        "source_url": "",
    }

    # Extract semester from path parts like "semester_3" or "sem3" or "3"
    for part in parts:
        sem_match = re.search(r"semester[_\s-]*(\d+)", part, re.IGNORECASE)
        if sem_match:
            metadata["semester"] = int(sem_match.group(1))
            continue

        # Bare number directory under "data"
        if re.match(r"^\d+$", part):
            idx = parts.index(part)
            if idx > 0 and "data" in parts[idx - 1].lower():
                metadata["semester"] = int(part)
                continue

    # Extract subject from directory name (the folder between semester and file)
    for i, part in enumerate(parts):
        if re.search(r"semester[_\s-]*\d+", part, re.IGNORECASE) or (
            re.match(r"^\d+$", part) and i > 0 and "data" in parts[i - 1].lower()
        ):
            # The next part should be the subject directory
            if i + 1 < len(parts) - 1:  # -1 because last part is filename
                metadata["subject"] = _format_subject_name(parts[i + 1])
                break


    # Extract unit number from filename
    unit_num = extract_unit_from_filename(metadata["source_filename"])
    if unit_num:
        metadata["unit_number"] = unit_num

    return metadata


def extract_unit_from_filename(filename: str) -> int:
    """
    Extract unit number from a filename.

    Examples:
      "unit2_slides.pptx" -> 2
      "Unit-3_Networks.pptx" -> 3
      "Module_1.pptx" -> 1
      "ch4_overview.pptx" -> 4
    """
    patterns = [
        r"unit[_\s-]*(\d+)",
        r"module[_\s-]*(\d+)",
        r"ch(?:apter)?[_\s-]*(\d+)",
        r"u(\d+)[_\s-]",
    ]

    name_lower = filename.lower()
    for pattern in patterns:
        match = re.search(pattern, name_lower)
        if match:
            return int(match.group(1))

    return 0


def extract_unit_from_content(text: str) -> int:
    """
    Try to extract unit number from slide content text.

    Looks for patterns like "Unit 3:", "UNIT III", "Module 2", etc.
    """
    patterns = [
        r"unit[:\s-]*(\d+)",
        r"unit[:\s-]*(i{1,4}v?|vi{0,3})",  # Roman numerals I-VIII
        r"module[:\s-]*(\d+)",
    ]

    text_lower = text.lower().strip()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            val = match.group(1)
            # Handle roman numerals
            roman = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8}
            if val in roman:
                return roman[val]
            try:
                return int(val)
            except ValueError:
                pass

    return 0


def _format_subject_name(dirname: str) -> str:
    """
    Convert a directory name back to a readable subject name.

    Example: "design_and_analysis_of_algorithms" -> "Design And Analysis Of Algorithms"
    """
    # Replace underscores and hyphens with spaces
    name = dirname.replace("_", " ").replace("-", " ")
    # Title case
    name = name.title()
    return name.strip()


def assign_slide_number(page_index: int) -> int:
    """
    Assign a 1-indexed slide number from a 0-indexed page index.
    """
    return page_index + 1


def enrich_metadata(
    base_metadata: dict,
    page_index: int = 0,
    content: str = "",
    source_url: str = "",
    manifest_data: Optional[dict] = None,
) -> dict:
    """
    Enrich metadata with additional information from content and manifest.

    Args:
        base_metadata: Metadata extracted from file path.
        page_index: 0-indexed page/slide number within the file.
        content: Slide text content (used to extract unit if not in filename).
        source_url: URL from the manifest.
        manifest_data: Full manifest dict for cross-referencing.

    Returns:
        Enriched metadata dict.
    """
    metadata = base_metadata.copy()
    metadata["slide_number"] = assign_slide_number(page_index)

    if source_url:
        metadata["source_url"] = source_url

    # Try to infer unit from content if not already set from filename
    if metadata.get("unit_number", 0) == 0 and content:
        unit = extract_unit_from_content(content)
        if unit:
            metadata["unit_number"] = unit

    # Cross-reference with manifest for source_url
    if manifest_data and not metadata.get("source_url"):
        url = _find_url_in_manifest(
            manifest_data,
            metadata.get("source_filename", ""),
            metadata.get("semester", 0),
        )
        if url:
            metadata["source_url"] = url

    return metadata


def _find_url_in_manifest(manifest: dict, filename: str, semester: int) -> str:
    """Look up source URL in manifest for a given file."""
    for subject in manifest.get("subjects", []):
        if subject.get("semester") != semester:
            continue
        for resource in subject.get("resources", []):
            local = resource.get("local_path", "")
            if local and os.path.basename(local) == filename:
                return resource.get("source_page_url", "")
    return ""
