import re
from typing import Dict, Any, Optional, List


class MetadataExtractor:
    """
    Extracts reliable academic curriculum metadata from text chunks.
    Adheres strictly to the rule: Never hallucinate metadata.
    Only populates fields when reliably present in the text.
    """

    SEMESTER_PATTERNS = [
        r'\b(?:Semester|Sem)\s*[:\-]?\s*([1-8]|I|II|III|IV|V|VI|VII|VIII)\b',
        r'\b([1-8])(?:st|nd|rd|th)?\s+Semester\b',
        r'\b(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth)\s+Semester\b',
        r'\b(?:in|for|of)?\s*sem(?:ester)?\s*([1-8])\b',
        r'\bwhat do i study in sem(?:ester)?\s*([1-8])\b',
    ]

    ROMAN_TO_NUM = {
        'i': 1, 'ii': 2, 'iii': 3, 'iv': 4,
        'v': 5, 'vi': 6, 'vii': 7, 'viii': 8,
        'first': 1, 'second': 2, 'third': 3, 'fourth': 4,
        'fifth': 5, 'sixth': 6, 'seventh': 7, 'eighth': 8,
    }

    # Matches course codes like CS101, CS301, CS207P, MA101, HS201, PE-I, OE-II, etc.
    COURSE_CODE_PATTERN = r'\b([A-Z]{2,4}[-\s]?[0-9]{3}[A-Z]?)\b'

    # Matches credits
    CREDIT_PATTERNS = [
        r'\bCredits?\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\b',
        r'\b([0-9]+(?:\.[0-9]+)?)\s*Credits?\b',
        r'\bTotal Credits[^:]*:\s*([0-9]+)\b',
    ]

    PREREQ_PATTERNS = [
        r'(?:Prerequisites?|Pre-requisites?)\s*[:\-]\s*([^\n;.]+)',
        r'\bPrereq\s*[:\-]\s*([^\n;.]+)',
    ]

    COURSE_TYPE_PATTERNS = [
        (r'\b(Professional Elective|Program Elective|PE)\b', "Professional Elective"),
        (r'\b(Open Elective|OE)\b', "Open Elective"),
        (r'\b(Core Course|Program Core|Professional Core|Core)\b', "Core"),
        (r'\b(Laboratory|Practical|Lab)\b', "Lab"),
        (r'\b(Humanities|HSMC)\b', "Humanities"),
        (r'\b(Mandatory Non-Credit|Audit Course)\b', "Audit / Non-Credit"),
    ]

    KNOWN_COURSES = [
        "Database Management Systems", "DBMS",
        "Data Structures and Algorithms", "Data Structures",
        "Operating Systems Principles", "Operating Systems",
        "Computer Organization and Architecture",
        "Discrete Mathematical Structures", "Discrete Mathematics",
        "Machine Learning",
        "Artificial Intelligence",
        "Computer Networks and Protocols", "Computer Networks",
        "Theory of Computation", "Automata",
        "Compiler Design Principles", "Compiler Design",
        "Data Science Fundamentals", "Data Science",
        "Cloud Computing Architecture", "Cloud Computing",
        "Cyber Security and Network Defense", "Cyber Security",
        "Big Data Analytics",
        "Software Engineering Principles", "Software Engineering",
        "Web Technologies and Full-Stack Frameworks", "Web Technologies",
        "Linear Algebra and Numerical Methods",
        "Probability and Statistics for Engineers",
        "Engineering Physics", "Engineering Chemistry",
        "Technical English Communication",
        "Introduction to Programming with C", "Object-Oriented Programming with Java"
    ]

    ORDINALS = {
        'first': 1, 'second': 2, 'third': 3, 'fourth': 4,
        'fifth': 5, 'sixth': 6, 'seventh': 7, 'eighth': 8,
        '1st': 1, '2nd': 2, '3rd': 3, '4th': 4,
        '5th': 5, '6th': 6, '7th': 7, '8th': 8,
    }
    ROMAN_NUMS = {
        'viii': 8, 'vii': 7, 'vi': 6, 'iv': 4, 'v': 5, 'iii': 3, 'ii': 2, 'i': 1
    }

    @classmethod
    def extract_semester(cls, text: str) -> Optional[int]:
        text_lower = text.lower()

        # 1. 'third semester', '3rd semester', '3rd sem' (must be followed by semester/sem)
        m = re.search(r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth|1st|2nd|3rd|4th|5th|6th|7th|8th)\s+sem(?:ester)?\b', text_lower)
        if m:
            return cls.ORDINALS.get(m.group(1))

        # 2. 'semester 3', 'sem 3', 'semester: 3', 'sem: 3', 'sem-3', 'semester-3'
        m = re.search(r'\b(?:semester|sem)\s*[:\-]?\s*([1-8])\b', text_lower)
        if m:
            return int(m.group(1))

        # 3. 'semester third', 'semester-iv', 'sem iii', 'semester iii'
        for r, num in cls.ROMAN_NUMS.items():
            if re.search(r'\b(?:semester|sem)\s*[:\-]?\s*' + r + r'\b', text_lower):
                return num

        # 4. 'what do i study in sem 3', 'in sem 3', 'sem 3 courses'
        m = re.search(r'\bsem(?:ester)?\s*([1-8])\b', text_lower)
        if m:
            return int(m.group(1))

        return None

    @classmethod
    def extract_course_codes(cls, text: str) -> List[str]:
        matches = re.findall(cls.COURSE_CODE_PATTERN, text)
        codes = []
        for m in matches:
            clean = re.sub(r'\s+', '', m).upper()
            if clean not in codes:
                codes.append(clean)
        return codes

    @classmethod
    def extract_course_names(cls, text: str) -> List[str]:
        """
        Extracts course names from table cells or structured syllabus lines.
        """
        names = []
        
        # 1. Check table rows: e.g. CS301 | Database Management Systems (DBMS) | ...
        for line in text.splitlines():
            if "|" in line:
                cells = [c.strip() for c in line.split("|")]
                if len(cells) >= 3:
                    # Usually cell 1 is Course Name
                    cell_name = cells[1]
                    if (
                        cell_name 
                        and not any(h in cell_name.lower() for h in ["course name", "subject name", "title"])
                        and len(cell_name) > 3
                    ):
                        if cell_name not in names:
                            names.append(cell_name)

        # 2. Check syllabus header pattern: Course Syllabus: CS301 - Database Management Systems (DBMS)
        match_syllabus = re.search(r'Course Syllabus:\s*[A-Z0-9]+\s*[–\-—]\s*([^\n(]+)', text)
        if match_syllabus:
            s_name = match_syllabus.group(1).strip()
            if s_name and s_name not in names:
                names.append(s_name)

        # 3. Check known curriculum courses explicitly mentioned
        text_lower = text.lower()
        for known in cls.KNOWN_COURSES:
            if known.lower() in text_lower and known not in names:
                names.append(known)

        return names

    @classmethod
    def extract_credits(cls, text: str) -> Optional[float]:
        for pattern in cls.CREDIT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None

    @classmethod
    def extract_prerequisites(cls, text: str) -> Optional[str]:
        # 1. From table row if row has Prerequisite column
        for line in text.splitlines():
            if "|" in line:
                cells = [c.strip() for c in line.split("|")]
                if len(cells) >= 4:
                    prereq_cell = cells[3]
                    if prereq_cell.lower() not in ["prerequisite", "prerequisites", "none", "nil", "-"]:
                        if len(prereq_cell) > 2:
                            return prereq_cell

        # 2. From standard text pattern
        for pattern in cls.PREREQ_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                res = match.group(1).strip()
                if res and res.lower() not in ["none", "nil", "n/a", "no", "-"]:
                    return res
                if res.lower() in ["none", "nil", "n/a", "no", "-"]:
                    return "None"
        return None

    @classmethod
    def extract_course_type(cls, text: str) -> Optional[str]:
        for pattern, label in cls.COURSE_TYPE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return label
        return None

    @classmethod
    def extract_department_program(cls, text: str) -> Dict[str, Optional[str]]:
        dept = None
        prog = None
        
        if re.search(r'\b(Computer Science|CSE|CS)\b', text, re.IGNORECASE):
            dept = "Computer Science and Engineering"
        elif re.search(r'\b(Information Technology|IT)\b', text, re.IGNORECASE):
            dept = "Information Technology"
        elif re.search(r'\b(Electronics and Communication|ECE)\b', text, re.IGNORECASE):
            dept = "Electronics and Communication Engineering"
        elif re.search(r'\b(Mechanical Engineering|ME)\b', text, re.IGNORECASE):
            dept = "Mechanical Engineering"
            
        if re.search(r'\b(B\.?Tech|Bachelor of Technology)\b', text, re.IGNORECASE):
            prog = "B.Tech"
        elif re.search(r'\b(M\.?Tech|Master of Technology)\b', text, re.IGNORECASE):
            prog = "M.Tech"
        elif re.search(r'\b(B\.?Sc|Bachelor of Science)\b', text, re.IGNORECASE):
            prog = "B.Sc"

        return {"department": dept, "program": prog}

    @classmethod
    def extract_academic_year(cls, text: str) -> Optional[str]:
        match = re.search(r'\b(202[0-9]\s*[-–]\s*202[0-9]|Regulations\s+202[0-9])\b', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    @classmethod
    def enrich_chunk(cls, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Populates chunk with all required metadata fields without hallucination:
        document, page, course code, course name, semester, credits, department/program,
        academic year, prerequisite.
        """
        text = chunk["text"]
        
        semester = cls.extract_semester(text)
        course_codes = cls.extract_course_codes(text)
        course_names = cls.extract_course_names(text)
        credits_val = cls.extract_credits(text)
        prereqs = cls.extract_prerequisites(text)
        course_type = cls.extract_course_type(text)
        dept_prog = cls.extract_department_program(text)
        acad_year = cls.extract_academic_year(text)

        chunk["metadata"] = {
            "document": chunk["filename"],
            "filename": chunk["filename"],
            "page": chunk["page_number"],
            "page_number": chunk["page_number"],
            "semester": semester,
            "course_code": course_codes[0] if course_codes else None,
            "course_codes": course_codes,
            "course_name": course_names[0] if course_names else None,
            "course_names": course_names,
            "credits": credits_val,
            "prerequisite": prereqs,
            "prerequisites": prereqs,
            "course_type": course_type,
            "department": dept_prog["department"],
            "program": dept_prog["program"],
            "academic_year": acad_year,
        }
        return chunk
