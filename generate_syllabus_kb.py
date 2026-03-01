"""
Generate comprehensive syllabus knowledge base documents for all SRM subjects.
Creates detailed topic-level text that can be embedded in ChromaDB for
syllabus-aware doubt clearing.

Each subject gets a rich document with unit topics, key concepts, and
keywords that will match student questions via semantic search.
"""

import json
import os
from langchain_core.documents import Document

SYLLABUS_KB = {
    # ═══════════════════════════════════════════════════════════════════
    # SEMESTER 1
    # ═══════════════════════════════════════════════════════════════════
    "Calculus And Linear Algebra": {
        "semester": 1,
        "units": {
            "Matrices": "Types of matrices, rank, echelon form, solving linear equations using Gauss elimination, Cayley-Hamilton theorem, eigenvalues and eigenvectors, diagonalization.",
            "Differential Calculus": "Limits, continuity, differentiation rules, Rolle's theorem, mean value theorems, Taylor and Maclaurin series, partial derivatives, total derivative, Jacobians.",
            "Integral Calculus": "Definite and indefinite integrals, reduction formulas, double and triple integrals, change of order of integration, beta and gamma functions.",
            "Multivariable Calculus": "Functions of several variables, maxima and minima, Lagrange multipliers, gradient, divergence, curl, line integrals, surface integrals.",
            "Linear Algebra": "Vector spaces, subspaces, linear independence, basis and dimension, linear transformations, inner product spaces, orthogonalization, Gram-Schmidt process."
        }
    },
    "Chemistry": {
        "semester": 1,
        "units": {
            "Atomic Structure": "Quantum numbers, orbitals, electron configuration, periodic properties, chemical bonding, VSEPR theory, molecular orbital theory.",
            "Thermodynamics": "Laws of thermodynamics, enthalpy, entropy, Gibbs free energy, chemical equilibrium, phase rule.",
            "Electrochemistry": "Electrochemical cells, Nernst equation, conductance, batteries and fuel cells, corrosion and its prevention.",
            "Polymers and Nanomaterials": "Types of polymerization, polymer properties, nanomaterials synthesis, carbon nanotubes, applications in engineering.",
            "Water Technology": "Water treatment processes, hardness, boiler troubles, desalination methods."
        }
    },
    "Philosophy Of Engineering": {
        "semester": 1,
        "units": {
            "Ethics in Engineering": "Professional ethics, moral responsibility, ethical dilemmas, codes of conduct, whistleblowing, safety and risk analysis.",
            "Environmental Ethics": "Sustainable development, environmental regulations, corporate social responsibility, green engineering.",
            "Engineering and Society": "Technology and society interaction, globalization effects, intellectual property rights, digital ethics.",
            "Human Values": "Morals, values, ethics distinction, value education, character building, universal human values.",
            "Professional Practices": "Engineering as profession, professional bodies, legal aspects, accountability."
        }
    },
    "Introduction To Computational Biology": {
        "semester": 1,
        "units": {
            "Biological Data": "DNA, RNA, proteins, sequences, biological databases like GenBank, UniProt, PDB.",
            "Sequence Analysis": "Sequence alignment, BLAST, dynamic programming for alignment, substitution matrices like BLOSUM and PAM.",
            "Phylogenetics": "Evolutionary trees, molecular evolution, phylogenetic methods, UPGMA, neighbor joining.",
            "Structural Biology": "Protein structure prediction, homology modeling, molecular visualization, Ramachandran plots.",
            "Genomics": "Genome sequencing, gene finding, functional genomics, comparative genomics, personalized medicine."
        }
    },
    "Programming For Problem Solving": {
        "semester": 1,
        "units": {
            "Introduction to C": "History of C, data types, variables, constants, operators, expressions, input/output functions printf scanf, type casting, storage classes.",
            "Control Structures": "Decision making if else switch, loops for while do-while, break continue goto, nested loops, problem solving with loops.",
            "Arrays and Strings": "One-dimensional arrays, two-dimensional arrays, string handling functions strlen strcpy strcat strcmp, character arrays, sorting and searching arrays.",
            "Functions and Pointers": "Function declaration definition calling, pass by value pass by reference, recursion, pointers and pointer arithmetic, pointers and arrays, dynamic memory allocation malloc calloc realloc free.",
            "Structures and File Handling": "Structure definition, array of structures, nested structures, unions, typedef, file operations fopen fclose fprintf fscanf, binary files."
        }
    },
    "Fundamental Of Economics (FOE)": {
        "semester": 1,
        "units": {
            "Microeconomics": "Demand and supply, elasticity, consumer equilibrium, indifference curves, production function, cost analysis.",
            "Market Structures": "Perfect competition, monopoly, oligopoly, monopolistic competition, pricing strategies.",
            "Macroeconomics": "National income accounting, GDP, inflation, monetary and fiscal policy, business cycles.",
            "Banking and Finance": "Banking system, central banking, money supply, interest rates, financial markets.",
            "Indian Economy": "Economic planning, liberalization, privatization, globalization, current economic issues."
        }
    },
    "Foreign Languages": {
        "semester": 1,
        "units": {
            "Language Basics": "Grammar, vocabulary, sentence construction, pronunciation, basic conversation.",
            "Reading Comprehension": "Text analysis, paragraph writing, summary writing, comprehension passages.",
            "Communication Skills": "Verbal and non-verbal communication, presentation skills, group discussion, interview skills.",
            "Writing Skills": "Essay writing, letter writing, report writing, email etiquette, technical writing.",
            "Cultural Studies": "Language and culture, traditions, festivals, literature overview."
        }
    },
    "Cell Biology": {
        "semester": 1,
        "units": {
            "Cell Structure": "Prokaryotic and eukaryotic cells, cell organelles, plasma membrane, nucleus, mitochondria, endoplasmic reticulum.",
            "Cell Division": "Mitosis, meiosis, cell cycle regulation, checkpoints, cyclins and CDKs, apoptosis.",
            "Cell Signaling": "Signal transduction pathways, receptors, second messengers, G-proteins, kinase cascades.",
            "Membrane Transport": "Diffusion, osmosis, active transport, ion channels, vesicular transport, endocytosis, exocytosis.",
            "Cell Biology Techniques": "Microscopy, cell fractionation, electrophoresis, chromatography, PCR, cell culture."
        }
    },

    # ═══════════════════════════════════════════════════════════════════
    # SEMESTER 2
    # ═══════════════════════════════════════════════════════════════════
    "Advanced Calculus And Complex Analysis": {
        "semester": 2,
        "units": {
            "Ordinary Differential Equations": "First order ODE, exact equations, linear ODE, Bernoulli equation, second order ODE with constant coefficients, method of variation of parameters.",
            "Laplace Transforms": "Definition, properties, inverse Laplace transform, convolution theorem, solving ODE using Laplace transforms, unit step function, Dirac delta function.",
            "Complex Analysis": "Complex numbers, analytic functions, Cauchy-Riemann equations, harmonic functions, conformal mapping, Mobius transformation.",
            "Complex Integration": "Cauchy integral theorem, Cauchy integral formula, Taylor series, Laurent series, singularities, residues, residue theorem.",
            "Applications": "Evaluation of real integrals using residues, argument principle, Rouche's theorem."
        }
    },
    "Electrical And Electronics Engineering": {
        "semester": 2,
        "units": {
            "DC Circuits": "Ohm's law, Kirchhoff's laws KVL KCL, mesh and nodal analysis, superposition theorem, Thevenin and Norton theorems, maximum power transfer.",
            "AC Circuits": "Alternating current fundamentals, phasors, impedance, RLC circuits, resonance, power factor, three-phase systems.",
            "Transformers and Machines": "Single phase transformer, principle, EMF equation, losses, efficiency, DC motors, DC generators, three-phase induction motor.",
            "Semiconductor Devices": "PN junction diode, Zener diode, BJT, FET, MOSFET, operational amplifier basics, rectifiers, voltage regulators.",
            "Digital Electronics Basics": "Number systems, logic gates AND OR NOT NAND NOR XOR, Boolean algebra, combinational circuits, flip-flops, counters."
        }
    },
    "Semiconductor Physics And Computational Methods": {
        "semester": 2,
        "units": {
            "Crystal Structure": "Bravais lattices, Miller indices, X-ray diffraction, Bragg's law, crystal defects.",
            "Quantum Mechanics": "Wave-particle duality, Schrodinger equation, particle in a box, hydrogen atom, quantum numbers.",
            "Band Theory": "Energy bands, conductors insulators semiconductors, Fermi-Dirac distribution, intrinsic and extrinsic semiconductors, Hall effect.",
            "Semiconductor Devices": "PN junction, depletion region, forward and reverse bias, Zener breakdown, LED, solar cell, photodiode.",
            "Computational Methods": "Numerical solutions of equations, interpolation, numerical integration, curve fitting, Monte Carlo methods."
        }
    },
    "Physics-Mechanics": {
        "semester": 2,
        "units": {
            "Mechanics": "Newton's laws, friction, work energy power, conservation laws, rotational motion, moment of inertia, angular momentum.",
            "Oscillations": "Simple harmonic motion SHM, damped oscillations, forced oscillations, resonance, coupled oscillators.",
            "Waves": "Transverse and longitudinal waves, wave equation, superposition, standing waves, beats, Doppler effect.",
            "Optics": "Interference, diffraction, polarization, lasers, fiber optics, holography.",
            "Modern Physics": "Special relativity, photoelectric effect, Compton effect, nuclear physics, radioactivity."
        }
    },
    "Object Oriented Design And Programming": {
        "semester": 2,
        "units": {
            "OOP Fundamentals": "Object-oriented paradigm, classes and objects, data abstraction, encapsulation, access specifiers public private protected, constructors and destructors, this pointer.",
            "Inheritance": "Types of inheritance single multiple multilevel hierarchical hybrid, base and derived classes, virtual base class, constructor calling order, method overriding.",
            "Polymorphism": "Function overloading, operator overloading, virtual functions, pure virtual functions, abstract classes, runtime polymorphism, vtable.",
            "Templates and Exception Handling": "Function templates, class templates, STL containers vector list map set, iterators, exception handling try catch throw, custom exceptions.",
            "Advanced OOP": "File handling in C++, friend functions and classes, static members, namespaces, smart pointers, RTTI, design patterns introduction."
        }
    },
    "Communicative English": {
        "semester": 2,
        "units": {
            "Grammar and Vocabulary": "Parts of speech, tenses, subject-verb agreement, articles, prepositions, common errors, vocabulary building, synonyms antonyms.",
            "Reading Skills": "Comprehension strategies, skimming, scanning, critical reading, summarizing, note-making.",
            "Writing Skills": "Paragraph writing, essay writing, formal and informal letters, report writing, email writing, resume and cover letter.",
            "Speaking Skills": "Pronunciation, intonation, public speaking, extempore, group discussion, mock interviews, debate skills.",
            "Technical Communication": "Technical report writing, proposal writing, research paper format, presentation skills, visual aids."
        }
    },
    "Electromagnetic Physics": {
        "semester": 2,
        "units": {
            "Electrostatics": "Coulomb's law, electric field, Gauss's law, electric potential, capacitors, dielectrics.",
            "Magnetostatics": "Biot-Savart law, Ampere's law, magnetic field, magnetic materials, inductance.",
            "Electromagnetic Induction": "Faraday's law, Lenz's law, self and mutual inductance, eddy currents, transformers.",
            "Maxwell's Equations": "Displacement current, Maxwell's equations in integral and differential form, electromagnetic waves.",
            "Wave Propagation": "Plane waves, polarization, reflection, refraction, waveguides, antenna basics."
        }
    },
    "Engineering Mechanics": {
        "semester": 2,
        "units": {
            "Statics": "Force systems, resultant, equilibrium, free body diagrams, Lami's theorem, support reactions.",
            "Friction": "Laws of friction, angle of friction, wedge friction, ladder friction, belt friction.",
            "Centroid and Moment of Inertia": "Centroid of composite areas, moment of inertia, parallel axis theorem, perpendicular axis theorem, radius of gyration.",
            "Dynamics": "Kinematics of particles, Newton's laws, D'Alembert's principle, work-energy principle, impulse-momentum.",
            "Virtual Work": "Principle of virtual work, stability of equilibrium, potential energy method."
        }
    },
    "Electronic System And PCB Design": {
        "semester": 2,
        "units": {
            "Electronic Components": "Resistors, capacitors, inductors, diodes, transistors, ICs, component selection.",
            "Circuit Design": "Schematic capture, circuit simulation, SPICE, amplifier design, filter design.",
            "PCB Design": "PCB layout, routing, design rules, gerber files, manufacturing process, surface mount vs through-hole.",
            "Embedded Systems": "Microcontroller basics, Arduino, sensor interfacing, actuator control, serial communication.",
            "Testing": "Multimeter usage, oscilloscope, signal generators, debugging techniques, quality assurance."
        }
    },

    # ═══════════════════════════════════════════════════════════════════
    # SEMESTER 3
    # ═══════════════════════════════════════════════════════════════════
    "Data Structures And Algorithm": {
        "semester": 3,
        "units": {
            "Arrays and Linked Lists": "Arrays operations traversal insertion deletion search, time complexity Big-O notation, singly linked list, doubly linked list, circular linked list, linked list operations, comparison of arrays and linked lists.",
            "Stacks and Queues": "Stack ADT LIFO, push pop peek operations, stack applications infix postfix prefix expression evaluation, queue ADT FIFO, circular queue, priority queue, deque, queue applications BFS CPU scheduling.",
            "Trees": "Binary tree, binary search tree BST, tree traversals inorder preorder postorder levelorder, AVL tree rotations, B-tree, B+ tree, heap min-heap max-heap, heapsort, Huffman coding.",
            "Graphs": "Graph representation adjacency matrix adjacency list, BFS breadth first search, DFS depth first search, shortest path Dijkstra Bellman-Ford, minimum spanning tree Prim Kruskal, topological sort, graph applications.",
            "Sorting and Searching": "Bubble sort, selection sort, insertion sort, merge sort, quick sort, radix sort, counting sort, binary search, hashing hash tables collision resolution chaining open addressing."
        }
    },
    "Computer Organization And Architecture": {
        "semester": 3,
        "units": {
            "Basic Computer Organization": "Von Neumann architecture, CPU structure, instruction cycle fetch decode execute, data path, control unit, registers, buses.",
            "Instruction Set Architecture": "Instruction formats, addressing modes immediate direct indirect register, RISC vs CISC, instruction pipelining, pipeline hazards.",
            "Memory System": "Memory hierarchy, cache memory direct mapped set associative fully associative, cache replacement policies LRU FIFO, virtual memory, page table, TLB, memory management.",
            "I/O Organization": "I/O techniques programmed I/O interrupt-driven I/O DMA, I/O processor, bus architecture, peripheral devices, interrupt handling.",
            "Processor Design": "ALU design, multiplier design, floating point representation IEEE 754, microprogramming, hardwired vs microprogrammed control."
        }
    },
    "Operating Systems": {
        "semester": 3,
        "units": {
            "OS Fundamentals": "Operating system types batch multiprogramming time-sharing real-time, system calls, OS structure monolithic layered microkernel, process concept, process states, PCB.",
            "Process Management": "CPU scheduling FCFS SJF priority round robin SRTF, process synchronization, critical section problem, mutex semaphore, deadlock detection prevention avoidance recovery, Banker's algorithm.",
            "Memory Management": "Contiguous allocation, paging, segmentation, virtual memory, demand paging, page replacement algorithms FIFO LRU optimal, thrashing, working set model.",
            "File Systems": "File concept, access methods sequential direct indexed, directory structure, file allocation contiguous linked indexed, free space management, disk scheduling FCFS SSTF SCAN C-SCAN.",
            "Advanced Topics": "Threads user-level kernel-level, multithreading models, inter-process communication IPC pipes message queues shared memory, Linux commands process management."
        }
    },
    "Transforms And Boundary Value Problems": {
        "semester": 3,
        "units": {
            "Fourier Series": "Fourier series representation, Dirichlet conditions, half range expansions, Parseval's theorem, harmonic analysis.",
            "Fourier Transform": "Fourier transform pairs, properties linearity shifting scaling, inverse Fourier transform, convolution theorem, applications to signal processing.",
            "Z-Transform": "Definition, properties, inverse Z-transform, solving difference equations, stability analysis.",
            "Partial Differential Equations": "Formation of PDE, solving first order PDE, classification elliptic parabolic hyperbolic, method of separation of variables.",
            "Boundary Value Problems": "One-dimensional wave equation, one-dimensional heat equation, two-dimensional Laplace equation, steady state and transient solutions."
        }
    },
    "Advanced Programming Practice": {
        "semester": 3,
        "units": {
            "Java Fundamentals": "Java features platform independence, JVM JDK JRE, data types, operators, control flow, arrays, strings, packages.",
            "OOP in Java": "Classes objects, inheritance, polymorphism, abstraction, interfaces, abstract classes, inner classes, access modifiers.",
            "Exception and I/O": "Exception handling try catch finally throw throws, custom exceptions, file I/O streams, serialization, collections framework.",
            "Multithreading": "Thread creation extending Thread implementing Runnable, thread lifecycle, synchronization, inter-thread communication wait notify.",
            "Advanced Java": "JDBC database connectivity, GUI Swing JavaFX basics, networking sockets, lambda expressions, generics."
        }
    },
    "Digital Logic Design": {
        "semester": 3,
        "units": {
            "Number Systems and Codes": "Binary octal hexadecimal, BCD Gray code, binary arithmetic, complements, signed number representation.",
            "Combinational Logic": "Boolean algebra, logic gates, Karnaugh map simplification, multiplexer, demultiplexer, encoder, decoder, adders half full ripple carry.",
            "Sequential Logic": "Flip-flops SR JK D T, triggering edge level, registers shift registers, counters synchronous asynchronous up down, state diagrams.",
            "Memory and PLDs": "ROM, RAM, PLA, PAL, FPGA, memory organization.",
            "Digital System Design": "Finite state machines Mealy Moore, ASM charts, design of digital systems, timing analysis."
        }
    },
    "Solid State Devices": {
        "semester": 3,
        "units": {
            "Semiconductor Fundamentals": "Crystal structure, energy bands, Fermi level, carrier concentration, drift and diffusion, carrier lifetime.",
            "PN Junction": "PN junction formation, depletion region, forward and reverse bias, breakdown mechanisms, junction capacitance.",
            "Bipolar Transistors": "BJT construction NPN PNP, modes of operation, current gain, CE CB CC configurations, biasing.",
            "Field Effect Transistors": "JFET, MOSFET enhancement depletion, CMOS technology, short channel effects.",
            "Optoelectronic Devices": "LED, photodiode, solar cell, laser diode, optical fiber communication."
        }
    },
    "Numerical Methods & Analysis": {
        "semester": 3,
        "units": {
            "Solutions of Equations": "Bisection method, Newton-Raphson method, secant method, fixed point iteration, convergence analysis.",
            "Interpolation": "Lagrange interpolation, Newton forward and backward interpolation, divided differences, spline interpolation.",
            "Numerical Differentiation and Integration": "Finite difference methods, trapezoidal rule, Simpson's 1/3 and 3/8 rules, Gaussian quadrature, Romberg integration.",
            "Numerical ODE": "Euler's method, modified Euler, Runge-Kutta methods RK2 RK4, predictor-corrector methods, stability.",
            "Linear Algebra Methods": "Gauss elimination, LU decomposition, iterative methods Jacobi Gauss-Seidel, eigenvalue computation power method."
        }
    },
    "Foundation of Data Science (FDS)": {
        "semester": 3,
        "units": {
            "Data Science Basics": "Data science lifecycle, types of data, data collection, data cleaning, exploratory data analysis EDA.",
            "Statistics": "Descriptive statistics mean median mode, probability distributions normal binomial Poisson, hypothesis testing, confidence intervals, correlation regression.",
            "Data Visualization": "Matplotlib, Seaborn, types of plots histogram scatter bar box, dashboard creation, storytelling with data.",
            "Machine Learning Intro": "Supervised vs unsupervised learning, classification, regression, clustering K-means, decision trees, model evaluation accuracy precision recall.",
            "Tools": "Python for data science, Pandas DataFrames, NumPy arrays, Jupyter notebooks, basic SQL for data queries."
        }
    },

    # ═══════════════════════════════════════════════════════════════════
    # SEMESTER 4
    # ═══════════════════════════════════════════════════════════════════
    "Design And Analysis Of Algorithms": {
        "semester": 4,
        "units": {
            "Algorithm Analysis": "Asymptotic notations Big-O Omega Theta, best average worst case, recurrence relations, Master theorem, amortized analysis.",
            "Divide and Conquer": "Merge sort, quick sort, binary search, Strassen's matrix multiplication, closest pair, maximum subarray problem.",
            "Greedy Algorithms": "Activity selection, Huffman coding, fractional knapsack, job sequencing, minimum spanning tree Prim Kruskal, Dijkstra's shortest path.",
            "Dynamic Programming": "Overlapping subproblems, optimal substructure, memoization vs tabulation, 0/1 knapsack, longest common subsequence LCS, matrix chain multiplication, Floyd-Warshall, edit distance.",
            "Backtracking and Branch & Bound": "N-Queens problem, subset sum, graph coloring, Hamiltonian cycle, branch and bound for TSP, NP-completeness, P vs NP, reductions."
        }
    },
    "Database Management Systems": {
        "semester": 4,
        "units": {
            "Introduction to DBMS": "Database concepts, DBMS vs file system, data models relational hierarchical network, three schema architecture, data independence.",
            "Relational Model": "Relations, keys primary candidate foreign super, relational algebra selection projection join division, relational calculus, SQL DDL DML DCL.",
            "SQL and Advanced Queries": "CREATE ALTER DROP, SELECT queries, joins inner outer left right, subqueries, aggregate functions GROUP BY HAVING, views, triggers, stored procedures.",
            "Normalization": "Functional dependencies, normal forms 1NF 2NF 3NF BCNF 4NF, decomposition, lossless join, dependency preservation.",
            "Transaction Management": "ACID properties, concurrency control, locking protocols two-phase locking, deadlock handling, serializability, recovery techniques."
        }
    },
    "Artificial Intelligence": {
        "semester": 4,
        "units": {
            "Introduction to AI": "AI history, intelligent agents, agent types simple reflex model-based goal-based utility-based, environment types, Turing test, AI applications.",
            "Search Algorithms": "Uninformed search BFS DFS DLS IDS UCS, informed search A* greedy best-first, heuristic functions, local search hill climbing simulated annealing genetic algorithms.",
            "Knowledge Representation": "Propositional logic, first-order predicate logic, resolution, unification, forward and backward chaining, semantic nets, frames.",
            "Machine Learning in AI": "Supervised learning, decision trees, neural networks, perceptron, backpropagation, unsupervised learning clustering, reinforcement learning basics.",
            "Natural Language Processing": "NLP basics, syntax and semantics, parsing, machine translation, chatbots, sentiment analysis, speech recognition."
        }
    },
    "Probability And Queueing Theory": {
        "semester": 4,
        "units": {
            "Probability": "Axioms of probability, conditional probability, Bayes theorem, random variables discrete continuous, probability distributions binomial Poisson geometric.",
            "Continuous Distributions": "Uniform, exponential, normal distribution, joint probability, marginal and conditional distributions, functions of random variables.",
            "Random Processes": "Classification of random processes, stationary processes, Markov chains, Chapman-Kolmogorov equations, steady state probabilities.",
            "Queueing Models": "M/M/1 queue, M/M/c queue, birth-death process, Little's formula, M/G/1 queue, finite capacity queues.",
            "Applications": "Network traffic modeling, call center optimization, CPU scheduling analysis, reliability engineering."
        }
    },
    "Internet Of Things (IOT)": {
        "semester": 4,
        "units": {
            "IoT Architecture": "IoT reference model, IoT protocols MQTT CoAP HTTP, IoT communication models, IoT vs M2M.",
            "Sensors and Actuators": "Types of sensors temperature humidity pressure motion, actuators motors relays, ADC DAC.",
            "IoT Platforms": "Arduino, Raspberry Pi, ESP32, cloud platforms AWS IoT Azure IoT, data collection and visualization.",
            "IoT Communication": "Wireless protocols WiFi Bluetooth Zigbee LoRa, cellular IoT, edge computing, fog computing.",
            "IoT Applications": "Smart home, smart city, healthcare IoT, industrial IoT IIoT, agriculture IoT, security challenges."
        }
    },

    # ═══════════════════════════════════════════════════════════════════
    # SEMESTER 5
    # ═══════════════════════════════════════════════════════════════════
    "Discrete Mathematics": {
        "semester": 5,
        "units": {
            "Logic and Proofs": "Propositional logic, logical connectives, truth tables, predicate logic, quantifiers, proof techniques direct indirect contradiction induction.",
            "Sets and Relations": "Set operations, power set, Cartesian product, relations properties reflexive symmetric transitive, equivalence relations, partial orders, Hasse diagrams.",
            "Functions and Counting": "Types of functions injective surjective bijective, pigeonhole principle, permutations combinations, binomial theorem, inclusion-exclusion principle.",
            "Graph Theory": "Graph types, isomorphism, Euler and Hamilton paths, planar graphs, graph coloring, chromatic number, trees spanning trees.",
            "Algebraic Structures": "Groups, subgroups, cyclic groups, permutation groups, cosets, Lagrange's theorem, rings, fields, lattices, Boolean algebra."
        }
    },
    "Full Stack Web Development": {
        "semester": 5,
        "units": {
            "Frontend": "HTML5 semantic elements, CSS3 flexbox grid, JavaScript ES6+, DOM manipulation, responsive design, React/Angular basics.",
            "Backend": "Node.js, Express.js, REST API design, routing, middleware, authentication JWT sessions, MVC pattern.",
            "Database": "SQL and NoSQL, MongoDB, CRUD operations, Mongoose ODM, database design, indexing.",
            "DevOps Basics": "Git version control, deployment Heroku Vercel Netlify, environment variables, CI/CD basics.",
            "Full Stack Project": "MERN stack, project structure, API integration, state management, testing, performance optimization."
        }
    },
    "Formal Language And Automata": {
        "semester": 5,
        "units": {
            "Finite Automata": "DFA, NFA, epsilon-NFA, equivalence of DFA and NFA, minimization of DFA, regular expressions, pumping lemma for regular languages.",
            "Context-Free Languages": "Context-free grammars CFG, derivation trees, ambiguity, simplification of CFG, Chomsky normal form CNF, Greibach normal form GNF.",
            "Pushdown Automata": "PDA definition, deterministic and non-deterministic PDA, equivalence of PDA and CFG, pumping lemma for CFL.",
            "Turing Machines": "Turing machine definition, TM as language acceptor, TM variants multi-tape multi-head, universal Turing machine, Church-Turing thesis.",
            "Computability": "Decidability, undecidability, halting problem, reducibility, Rice's theorem, complexity classes P NP NP-complete."
        }
    },
    "Computer Networks": {
        "semester": 5,
        "units": {
            "Network Fundamentals": "OSI model 7 layers, TCP/IP model, network topologies star bus ring mesh, transmission media, network devices hub switch router.",
            "Data Link Layer": "Framing, error detection CRC checksum, error correction Hamming code, flow control stop-and-wait sliding window, MAC protocols ALOHA CSMA/CD.",
            "Network Layer": "IP addressing IPv4 IPv6, subnetting CIDR, routing algorithms distance vector link state, RIP OSPF BGP, ICMP, ARP.",
            "Transport Layer": "TCP connection management three-way handshake, TCP flow control congestion control, UDP, port numbers, socket programming.",
            "Application Layer": "DNS, HTTP HTTPS, FTP, SMTP POP3 IMAP, DHCP, network security SSL/TLS, firewalls, VPN, cryptography basics."
        }
    },
    "Machine Learning": {
        "semester": 5,
        "units": {
            "ML Fundamentals": "Types of learning supervised unsupervised reinforcement, training testing validation, bias-variance tradeoff, overfitting underfitting, cross-validation.",
            "Regression": "Linear regression, multiple regression, polynomial regression, gradient descent, regularization L1 L2, evaluation metrics MSE RMSE R-squared.",
            "Classification": "Logistic regression, decision trees, random forests, SVM support vector machines, KNN, Naive Bayes, evaluation metrics accuracy precision recall F1 AUC-ROC.",
            "Unsupervised Learning": "K-means clustering, hierarchical clustering, DBSCAN, PCA principal component analysis, dimensionality reduction, association rules Apriori.",
            "Deep Learning Intro": "Neural networks, activation functions sigmoid ReLU, backpropagation, CNN convolutional neural networks, RNN recurrent neural networks, applications."
        }
    },

    # ═══════════════════════════════════════════════════════════════════
    # SEMESTER 6
    # ═══════════════════════════════════════════════════════════════════
    "Data Science": {
        "semester": 6,
        "units": {
            "Data Wrangling": "Data cleaning, missing values handling, outlier detection, feature engineering, data transformation, ETL pipelines.",
            "Statistical Analysis": "Hypothesis testing t-test chi-square ANOVA, correlation analysis, regression analysis, time series analysis.",
            "Big Data": "Hadoop ecosystem, MapReduce, HDFS, Spark, NoSQL databases, data warehousing, data lakes.",
            "Visualization and Reporting": "Advanced visualization Tableau Power BI, interactive dashboards, data storytelling, business intelligence.",
            "ML Applications": "Predictive analytics, recommendation systems, text analytics, sentiment analysis, A/B testing."
        }
    },
    "Software Engineering And Project Management": {
        "semester": 6,
        "units": {
            "Software Process": "Software development lifecycle SDLC, waterfall model, agile Scrum Kanban, spiral model, V-model, DevOps.",
            "Requirements Engineering": "Requirements elicitation, analysis, specification SRS, validation, use case diagrams, user stories.",
            "Design": "Software design principles SOLID, architectural patterns MVC MVP microservices, UML diagrams class sequence activity.",
            "Testing": "Testing levels unit integration system acceptance, black box white box testing, test case design, automation testing, code coverage.",
            "Project Management": "Estimation COCOMO function points, scheduling Gantt PERT CPM, risk management, quality assurance CMM, configuration management."
        }
    },
    "Compiler Design": {
        "semester": 6,
        "units": {
            "Lexical Analysis": "Tokens, lexemes, patterns, regular expressions, finite automata for scanner, LEX tool, symbol table.",
            "Syntax Analysis": "Context-free grammars, parsing top-down bottom-up, recursive descent, LL(1) parser, LR(0) SLR LALR CLR parsers, YACC tool.",
            "Semantic Analysis": "Syntax-directed translation, attribute grammars, type checking, type conversions, intermediate code generation three-address code.",
            "Code Optimization": "Basic blocks, flow graphs, optimization techniques constant folding dead code elimination loop optimization, peephole optimization.",
            "Code Generation": "Target machine code, register allocation, instruction selection, instruction scheduling."
        }
    },

    # ═══════════════════════════════════════════════════════════════════
    # ADDITIONAL SUBJECTS (cross-department)
    # ═══════════════════════════════════════════════════════════════════
    "Design Thinking And Methodology": {
        "semester": 3,
        "units": {
            "Design Thinking": "Empathize, define, ideate, prototype, test. Human-centered design, design sprints.",
            "Innovation": "Types of innovation, creative problem solving, brainstorming techniques, SCAMPER, mind mapping."
        }
    },
    "Biomedical Sensors": {
        "semester": 1,
        "units": {
            "Biosensors": "Types of biosensors, electrochemical, optical, piezoelectric, temperature sensors, pressure sensors.",
            "Medical Instrumentation": "ECG, EEG, EMG, blood pressure measurement, pulse oximetry, medical imaging."
        }
    },
    "Social Engineering": {
        "semester": 3,
        "units": {
            "Social Analysis": "Social structures, community development, social research methods, survey design.",
            "Engineering Ethics": "Professional responsibility, sustainability, technology and society impact."
        }
    },
    "Electromagnetic Thoery And Interference": {
        "semester": 3,
        "units": {
            "EM Theory": "Maxwell's equations, wave propagation, polarization, transmission lines, waveguides, antennas.",
            "Interference": "Young's double slit, thin film interference, Michelson interferometer, Fabry-Perot interferometer."
        }
    },
    "Basic Chemical Engineering": {
        "semester": 3,
        "units": {
            "Process Calculations": "Material balance, energy balance, stoichiometry, process flow diagrams.",
            "Unit Operations": "Fluid mechanics, heat transfer, mass transfer, distillation, absorption."
        }
    },
    "Genetics And Cytogenetics": {
        "semester": 3,
        "units": {
            "Genetics": "Mendelian genetics, linkage, crossing over, gene mapping, DNA replication, transcription, translation.",
            "Cytogenetics": "Chromosome structure, karyotyping, chromosomal aberrations, polyploidy, genetic disorders."
        }
    },
    "Software Process": {
        "semester": 4,
        "units": {
            "Process Models": "Waterfall, agile, Scrum, Kanban, extreme programming, software process improvement CMM CMMI.",
            "Quality Assurance": "Software quality metrics, testing strategies, code review, continuous integration."
        }
    },
    "Chemical Engineering Principles": {
        "semester": 4,
        "units": {
            "Thermodynamics": "First and second law applied to chemical processes, phase equilibria, chemical equilibrium.",
            "Reaction Engineering": "Reaction kinetics, reactor design batch CSTR PFR, conversion, selectivity."
        }
    },
    "Molecular Biology": {
        "semester": 4,
        "units": {
            "DNA and Gene Expression": "DNA structure, replication, transcription, RNA processing, translation, genetic code.",
            "Gene Regulation": "Operons, gene regulation in prokaryotes and eukaryotes, epigenetics, gene therapy."
        }
    },
    "Cell Communication And Signaling": {
        "semester": 4,
        "units": {
            "Signal Transduction": "Cell surface receptors, G-protein coupled receptors, receptor tyrosine kinases, second messengers.",
            "Pathways": "MAPK pathway, PI3K/Akt pathway, Wnt signaling, Notch signaling, apoptosis pathways."
        }
    },
    "Bioprocess Engineering": {
        "semester": 4,
        "units": {
            "Fermentation": "Microbial growth kinetics, batch and continuous fermentation, bioreactor design.",
            "Downstream Processing": "Cell disruption, filtration, centrifugation, chromatography, product recovery."
        }
    },
    "Physical And Analytical Chemistry": {
        "semester": 1,
        "units": {
            "Physical Chemistry": "Chemical kinetics, surface chemistry, colloidal chemistry, photochemistry.",
            "Analytical Chemistry": "Qualitative and quantitative analysis, spectroscopy UV-Vis IR NMR, chromatography."
        }
    },
    "Biochemistry": {
        "semester": 1,
        "units": {
            "Biomolecules": "Carbohydrates, lipids, proteins, nucleic acids, vitamins, enzymes.",
            "Metabolism": "Glycolysis, Krebs cycle, electron transport chain, fatty acid oxidation, amino acid metabolism."
        }
    },
    "Behavioral Psychology": {
        "semester": 7,
        "units": {
            "Psychology Fundamentals": "Learning theories, motivation, personality, stress management, emotional intelligence.",
            "Organizational Behavior": "Group dynamics, leadership, communication, conflict resolution, team building."
        }
    },
    "Bioprocess Principles": {
        "semester": 3,
        "units": {
            "Bioprocess": "Sterilization, media preparation, microbial growth, fermentation technology.",
            "Bioprocess Design": "Scale-up, bioprocess economics, regulatory aspects, GMP."
        }
    },
    "Microbiology": {
        "semester": 1,
        "units": {
            "Microbial World": "Bacteria, viruses, fungi, protozoa, classification, morphology, growth.",
            "Applied Microbiology": "Sterilization, antibiotics, food microbiology, environmental microbiology, industrial microbiology."
        }
    },
    "Basic Civil & Mechanical Workshop": {
        "semester": 1,
        "units": {
            "Civil Workshop": "Surveying basics, building materials, construction techniques, plumbing, carpentry.",
            "Mechanical Workshop": "Fitting, welding, sheet metal work, foundry, machine shop basics."
        }
    },
}


def generate_documents():
    """Generate LangChain Documents from the syllabus knowledge base."""
    docs = []
    for subject, info in SYLLABUS_KB.items():
        semester = info["semester"]
        for unit_name, unit_content in info["units"].items():
            # Create a rich document for each unit
            text = (
                f"Subject: {subject} | Semester: {semester} | Unit: {unit_name}\n\n"
                f"Key Topics and Concepts:\n{unit_content}\n\n"
                f"This unit covers the following in the {subject} course "
                f"(Semester {semester}) at SRM Institute of Science and Technology."
            )
            doc = Document(
                page_content=text,
                metadata={
                    "subject": subject,
                    "semester": semester,
                    "unit_name": unit_name,
                    "source_filename": f"syllabus_sem{semester}_{subject.lower().replace(' ', '_')}.txt",
                    "slide_number": 1,
                    "source_type": "syllabus_kb",
                }
            )
            docs.append(doc)
    return docs


if __name__ == "__main__":
    docs = generate_documents()
    print(f"Generated {len(docs)} syllabus documents")
    print(f"Subjects covered: {len(SYLLABUS_KB)}")
    sems = set(info['semester'] for info in SYLLABUS_KB.values())
    print(f"Semesters covered: {sorted(sems)}")
    for sem in sorted(sems):
        subjs = [s for s, i in SYLLABUS_KB.items() if i['semester'] == sem]
        print(f"  Semester {sem}: {len(subjs)} subjects")
