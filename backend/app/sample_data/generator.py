import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_sample_curriculum_pdf(output_path: str | Path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
        alignment=1,
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=20
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155")
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold"
    )

    story = []

    # ================= PAGE 1 =================
    story.append(Paragraph("APEX INSTITUTE OF TECHNOLOGY & SCIENCE", title_style))
    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING<br/><b>Bachelor of Technology (B.Tech) — Curriculum & Regulations (2024–2028)</b>", subtitle_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. Program Overview and Academic Regulations", h1_style))
    overview_text = (
        "The B.Tech in Computer Science and Engineering (CSE) is a 4-year (8 semesters) undergraduate program "
        "designed in alignment with standard AICTE university guidelines. The program aims to equip students "
        "with strong foundational concepts in computing systems, algorithmic problem solving, software engineering, "
        "data science, and generative artificial intelligence."
    )
    story.append(Paragraph(overview_text, body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Graduation and Credit Requirements", h1_style))
    credit_summary_data = [
        [Paragraph("Category", table_cell_bold), Paragraph("Category Description", table_cell_bold), Paragraph("Required Credits", table_cell_bold)],
        [Paragraph("PC", table_cell), Paragraph("Program Professional Core Courses", table_cell), Paragraph("68", table_cell)],
        [Paragraph("PE", table_cell), Paragraph("Professional Elective Courses", table_cell), Paragraph("18", table_cell)],
        [Paragraph("OE", table_cell), Paragraph("Open University Electives", table_cell), Paragraph("12", table_cell)],
        [Paragraph("BS", table_cell), Paragraph("Basic Science Courses (Maths, Physics)", table_cell), Paragraph("24", table_cell)],
        [Paragraph("ES", table_cell), Paragraph("Engineering Science Courses", table_cell), Paragraph("18", table_cell)],
        [Paragraph("HSMC", table_cell), Paragraph("Humanities, Social Sciences & Management", table_cell), Paragraph("10", table_cell)],
        [Paragraph("PROJ", table_cell), Paragraph("Capstone Major Projects & Internship", table_cell), Paragraph("16", table_cell)],
        [Paragraph("Total", table_cell_bold), Paragraph("Minimum Total Credits for Degree Completion", table_cell_bold), Paragraph("166 Credits", table_cell_bold)],
    ]
    t1 = Table(credit_summary_data, colWidths=[60, 360, 110])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t1)
    story.append(Spacer(1, 12))

    story.append(Paragraph("3. Academic Regulations and Attendance Policy", h1_style))
    reg_text = (
        "• <b>Minimum Attendance Requirement:</b> A student must maintain a minimum of 75% attendance in each course.<br/>"
        "• <b>Passing Criteria:</b> A minimum of 40% aggregate marks in continuous internal evaluations and end-semester examinations.<br/>"
        "• <b>Grading Scale:</b> Standard 10-point scale: O (10), A+ (9), A (8), B+ (7), B (6), C (5), F (0)."
    )
    story.append(Paragraph(reg_text, body_style))
    story.append(PageBreak())

    # ================= PAGE 2 =================
    story.append(Paragraph("Department of Computer Science and Engineering — First Year Structure", title_style))
    story.append(Paragraph("<b>Semester 1 Course Structure</b>", h1_style))
    sem1_data = [
        [Paragraph("Course Code", table_cell_bold), Paragraph("Course Name", table_cell_bold), Paragraph("Type", table_cell_bold), Paragraph("Prerequisite", table_cell_bold), Paragraph("Credits", table_cell_bold)],
        [Paragraph("CS101", table_cell), Paragraph("Introduction to Programming with C", table_cell), Paragraph("Core", table_cell), Paragraph("None", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("MA101", table_cell), Paragraph("Engineering Mathematics I (Calculus & Matrices)", table_cell), Paragraph("Basic Science", table_cell), Paragraph("None", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("PH101", table_cell), Paragraph("Engineering Physics", table_cell), Paragraph("Basic Science", table_cell), Paragraph("None", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("EE101", table_cell), Paragraph("Basic Electrical & Electronics Engineering", table_cell), Paragraph("Engineering Sci", table_cell), Paragraph("None", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("HS101", table_cell), Paragraph("Technical English Communication", table_cell), Paragraph("Humanities", table_cell), Paragraph("None", table_cell), Paragraph("2 Credits", table_cell)],
        [Paragraph("CS101P", table_cell), Paragraph("C Programming Laboratory", table_cell), Paragraph("Lab", table_cell), Paragraph("None", table_cell), Paragraph("1.5 Credits", table_cell)],
        [Paragraph("PH101P", table_cell), Paragraph("Physics Laboratory", table_cell), Paragraph("Lab", table_cell), Paragraph("None", table_cell), Paragraph("1.5 Credits", table_cell)],
    ]
    t_sem1 = Table(sem1_data, colWidths=[70, 200, 90, 90, 80])
    t_sem1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sem1)
    story.append(Paragraph("<b>Total Credits in Semester 1: 19 Credits</b>", body_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>Semester 2 Course Structure</b>", h1_style))
    sem2_data = [
        [Paragraph("Course Code", table_cell_bold), Paragraph("Course Name", table_cell_bold), Paragraph("Type", table_cell_bold), Paragraph("Prerequisite", table_cell_bold), Paragraph("Credits", table_cell_bold)],
        [Paragraph("CS102", table_cell), Paragraph("Data Structures and Algorithms", table_cell), Paragraph("Core", table_cell), Paragraph("CS101 (Programming)", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("MA102", table_cell), Paragraph("Engineering Mathematics II (Differential Equations)", table_cell), Paragraph("Basic Science", table_cell), Paragraph("MA101", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("CS103", table_cell), Paragraph("Digital Logic & System Design", table_cell), Paragraph("Core", table_cell), Paragraph("None", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("CH101", table_cell), Paragraph("Environmental Science & Chemistry", table_cell), Paragraph("Basic Science", table_cell), Paragraph("None", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("ME101", table_cell), Paragraph("Engineering Graphics and Design", table_cell), Paragraph("Engineering Sci", table_cell), Paragraph("None", table_cell), Paragraph("2 Credits", table_cell)],
        [Paragraph("CS102P", table_cell), Paragraph("Data Structures Laboratory", table_cell), Paragraph("Lab", table_cell), Paragraph("CS101", table_cell), Paragraph("2 Credits", table_cell)],
    ]
    t_sem2 = Table(sem2_data, colWidths=[70, 200, 90, 90, 80])
    t_sem2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sem2)
    story.append(Paragraph("<b>Total Credits in Semester 2: 18 Credits</b>", body_style))
    story.append(PageBreak())

    # ================= PAGE 3 =================
    story.append(Paragraph("Department of Computer Science and Engineering — Second Year Structure", title_style))
    story.append(Paragraph("<b>Semester 3 Course Structure (Third Semester)</b>", h1_style))
    sem3_data = [
        [Paragraph("Course Code", table_cell_bold), Paragraph("Course Name", table_cell_bold), Paragraph("Type", table_cell_bold), Paragraph("Prerequisite", table_cell_bold), Paragraph("Credits", table_cell_bold)],
        [Paragraph("CS201", table_cell), Paragraph("Discrete Mathematical Structures", table_cell), Paragraph("Core", table_cell), Paragraph("MA101", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("CS202", table_cell), Paragraph("Object-Oriented Programming with Java", table_cell), Paragraph("Core", table_cell), Paragraph("CS101 (Programming in C)", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("CS301", table_cell), Paragraph("Database Management Systems (DBMS)", table_cell), Paragraph("Core", table_cell), Paragraph("CS102 (Data Structures)", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("CS204", table_cell), Paragraph("Computer Organization and Architecture", table_cell), Paragraph("Core", table_cell), Paragraph("CS103 (Digital Logic)", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("MA201", table_cell), Paragraph("Linear Algebra and Numerical Methods", table_cell), Paragraph("Basic Science", table_cell), Paragraph("MA101", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("CS301P", table_cell), Paragraph("DBMS and SQL Laboratory", table_cell), Paragraph("Lab", table_cell), Paragraph("CS102", table_cell), Paragraph("1.5 Credits", table_cell)],
        [Paragraph("CS202P", table_cell), Paragraph("Java OOP Laboratory", table_cell), Paragraph("Lab", table_cell), Paragraph("CS101", table_cell), Paragraph("1.5 Credits", table_cell)],
    ]
    t_sem3 = Table(sem3_data, colWidths=[70, 200, 90, 90, 80])
    t_sem3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sem3)
    story.append(Paragraph("<b>Total Credits in Semester 3 (Third Semester): 21 Credits</b>", body_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>Semester 4 Course Structure (Fourth Semester)</b>", h1_style))
    sem4_data = [
        [Paragraph("Course Code", table_cell_bold), Paragraph("Course Name", table_cell_bold), Paragraph("Type", table_cell_bold), Paragraph("Prerequisite", table_cell_bold), Paragraph("Credits", table_cell_bold)],
        [Paragraph("CS207", table_cell), Paragraph("Operating Systems Principles", table_cell), Paragraph("Core", table_cell), Paragraph("CS102 & CS204", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("CS208", table_cell), Paragraph("Design and Analysis of Algorithms", table_cell), Paragraph("Core", table_cell), Paragraph("CS102 (Data Structures)", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("CS209", table_cell), Paragraph("Software Engineering Principles & Agile", table_cell), Paragraph("Core", table_cell), Paragraph("None", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("MA202", table_cell), Paragraph("Probability and Statistics for Engineers", table_cell), Paragraph("Basic Science", table_cell), Paragraph("MA101", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("HS201", table_cell), Paragraph("Universal Human Values and Ethics", table_cell), Paragraph("Humanities", table_cell), Paragraph("None", table_cell), Paragraph("2 Credits", table_cell)],
        [Paragraph("CS207P", table_cell), Paragraph("Operating Systems & Linux Shell Lab", table_cell), Paragraph("Lab", table_cell), Paragraph("CS101", table_cell), Paragraph("1.5 Credits", table_cell)],
        [Paragraph("CS208P", table_cell), Paragraph("Algorithms Implementation Lab", table_cell), Paragraph("Lab", table_cell), Paragraph("CS102", table_cell), Paragraph("1.5 Credits", table_cell)],
    ]
    t_sem4 = Table(sem4_data, colWidths=[70, 200, 90, 90, 80])
    t_sem4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sem4)
    story.append(Paragraph("<b>Total Credits in Semester 4 (Fourth Semester): 19 Credits</b> (Overall Year 2 Credits: 40 Credits)", body_style))
    story.append(PageBreak())

    # ================= PAGE 4 =================
    story.append(Paragraph("Department of Computer Science and Engineering — Third Year Structure", title_style))
    story.append(Paragraph("<b>Semester 5 Course Structure & Professional Electives</b>", h1_style))
    sem5_data = [
        [Paragraph("Course Code", table_cell_bold), Paragraph("Course Name", table_cell_bold), Paragraph("Type", table_cell_bold), Paragraph("Prerequisite", table_cell_bold), Paragraph("Credits", table_cell_bold)],
        [Paragraph("CS302", table_cell), Paragraph("Computer Networks and Protocols", table_cell), Paragraph("Core", table_cell), Paragraph("CS207 (Operating Systems)", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("CS303", table_cell), Paragraph("Theory of Computation and Automata", table_cell), Paragraph("Core", table_cell), Paragraph("CS201 (Discrete Math)", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("CS305", table_cell), Paragraph("Machine Learning", table_cell), Paragraph("Core", table_cell), Paragraph("MA202 (Prob & Stats) & CS102", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("PE-I", table_cell), Paragraph("Professional Elective I (List below)", table_cell), Paragraph("Professional Elective", table_cell), Paragraph("As per elective", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("OE-I", table_cell), Paragraph("Open Elective I (University-wide)", table_cell), Paragraph("Open Elective", table_cell), Paragraph("None", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("CS302P", table_cell), Paragraph("Computer Networks & Packet Tracing Lab", table_cell), Paragraph("Lab", table_cell), Paragraph("CS207", table_cell), Paragraph("1.5 Credits", table_cell)],
        [Paragraph("CS305P", table_cell), Paragraph("Machine Learning with Python Lab", table_cell), Paragraph("Lab", table_cell), Paragraph("CS102", table_cell), Paragraph("1.5 Credits", table_cell)],
    ]
    t_sem5 = Table(sem5_data, colWidths=[70, 200, 90, 90, 80])
    t_sem5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sem5)
    story.append(Paragraph("<b>Total Credits in Semester 5: 20 Credits</b>", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Professional Elective Basket I (Available in Semester 5)</b>", h1_style))
    pe1_data = [
        [Paragraph("Course Code", table_cell_bold), Paragraph("Elective Subject Name", table_cell_bold), Paragraph("Prerequisites", table_cell_bold), Paragraph("Credits", table_cell_bold)],
        [Paragraph("CS311", table_cell), Paragraph("Data Science Fundamentals", table_cell), Paragraph("CS101 (Programming) or Python", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("CS312", table_cell), Paragraph("Cloud Computing Architecture & AWS", table_cell), Paragraph("CS207 (Operating Systems)", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("CS313", table_cell), Paragraph("Cyber Security and Network Defense", table_cell), Paragraph("CS207 & CS302 (Networks)", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("CS314", table_cell), Paragraph("Computer Graphics and Virtual Reality", table_cell), Paragraph("CS102 & MA201 (Linear Algebra)", table_cell), Paragraph("3 Credits", table_cell)],
    ]
    t_pe1 = Table(pe1_data, colWidths=[70, 200, 160, 100])
    t_pe1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_pe1)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Semester 6 Course Structure</b>", h1_style))
    sem6_data = [
        [Paragraph("Course Code", table_cell_bold), Paragraph("Course Name", table_cell_bold), Paragraph("Type", table_cell_bold), Paragraph("Prerequisite", table_cell_bold), Paragraph("Credits", table_cell_bold)],
        [Paragraph("CS306", table_cell), Paragraph("Compiler Design Principles", table_cell), Paragraph("Core", table_cell), Paragraph("CS303 (Theory of Computation)", table_cell), Paragraph("4 Credits", table_cell)],
        [Paragraph("CS307", table_cell), Paragraph("Web Technologies and Full-Stack Frameworks", table_cell), Paragraph("Core", table_cell), Paragraph("CS202 (Java OOP)", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("PE-II", table_cell), Paragraph("Professional Elective II (NLP / Deep Learning / IoT)", table_cell), Paragraph("Professional Elective", table_cell), Paragraph("CS305", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("PE-III", table_cell), Paragraph("Professional Elective III (Distributed Systems / DevOps)", table_cell), Paragraph("Professional Elective", table_cell), Paragraph("CS207", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("OE-II", table_cell), Paragraph("Open Elective II", table_cell), Paragraph("Open Elective", table_cell), Paragraph("None", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("CS308P", table_cell), Paragraph("Mini Project and Design Thinking", table_cell), Paragraph("Project", table_cell), Paragraph("CS301 & CS209", table_cell), Paragraph("2 Credits", table_cell)],
    ]
    t_sem6 = Table(sem6_data, colWidths=[70, 200, 90, 90, 80])
    t_sem6.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sem6)
    story.append(Paragraph("<b>Total Credits in Semester 6: 18 Credits</b>", body_style))
    story.append(PageBreak())

    # ================= PAGE 5 =================
    story.append(Paragraph("Department of Computer Science and Engineering — Final Year Structure", title_style))
    story.append(Paragraph("<b>Semester 7 Course Structure</b>", h1_style))
    sem7_data = [
        [Paragraph("Course Code", table_cell_bold), Paragraph("Course Name", table_cell_bold), Paragraph("Type", table_cell_bold), Paragraph("Prerequisite", table_cell_bold), Paragraph("Credits", table_cell_bold)],
        [Paragraph("CS401", table_cell), Paragraph("Big Data Analytics & Distributed Computing", table_cell), Paragraph("Core", table_cell), Paragraph("CS301 (DBMS) & CS311", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("PE-IV", table_cell), Paragraph("Professional Elective IV (Generative AI / Robotics)", table_cell), Paragraph("Professional Elective", table_cell), Paragraph("CS305", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("PE-V", table_cell), Paragraph("Professional Elective V (Quantum Computing / Blockchain)", table_cell), Paragraph("Professional Elective", table_cell), Paragraph("CS208", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("OE-III", table_cell), Paragraph("Open Elective III: Financial Engineering", table_cell), Paragraph("Open Elective", table_cell), Paragraph("None", table_cell), Paragraph("3 Credits", table_cell)],
        [Paragraph("CS402", table_cell), Paragraph("Capstone Major Project Phase I", table_cell), Paragraph("Core Project", table_cell), Paragraph("All prior core courses", table_cell), Paragraph("5 Credits", table_cell)],
    ]
    t_sem7 = Table(sem7_data, colWidths=[70, 200, 90, 90, 80])
    t_sem7.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sem7)
    story.append(Paragraph("<b>Total Credits in Semester 7: 17 Credits</b>", body_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>Semester 8 Course Structure (Final Semester)</b>", h1_style))
    sem8_data = [
        [Paragraph("Course Code", table_cell_bold), Paragraph("Course Name", table_cell_bold), Paragraph("Type", table_cell_bold), Paragraph("Prerequisite", table_cell_bold), Paragraph("Credits", table_cell_bold)],
        [Paragraph("CS403", table_cell), Paragraph("Capstone Major Project Phase II / Industrial Internship", table_cell), Paragraph("Core Project", table_cell), Paragraph("CS402", table_cell), Paragraph("10 Credits", table_cell)],
        [Paragraph("PE-VI", table_cell), Paragraph("Professional Elective VI (Self-Paced / MOOC Online)", table_cell), Paragraph("Professional Elective", table_cell), Paragraph("Department approval", table_cell), Paragraph("3 Credits", table_cell)],
    ]
    t_sem8 = Table(sem8_data, colWidths=[70, 200, 90, 90, 80])
    t_sem8.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sem8)
    story.append(Paragraph("<b>Total Credits in Semester 8: 13 Credits</b><br/><b>Grand Total Degree Credits: 166 Credits</b>", body_style))
    story.append(PageBreak())

    # ================= PAGE 6 =================
    story.append(Paragraph("Detailed Course Syllabi and Examination Regulations", title_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Course Syllabus: CS301 — Database Management Systems (DBMS)", h1_style))
    cs301_text = (
        "<b>Course Code:</b> CS301 | <b>Credits:</b> 4 Credits (L-T-P: 3-1-0) | <b>Semester:</b> Third Semester (Semester 3)<br/>"
        "<b>Course Type:</b> Professional Core | <b>Prerequisites:</b> CS102 Data Structures and Algorithms.<br/>"
        "<b>Syllabus Modules:</b><br/>"
        "• <b>Module 1 (Foundations):</b> Database System Concepts, 3-tier Schema Architecture, Data Independence, Entity-Relationship (ER) Modeling, Extended ER.<br/>"
        "• <b>Module 2 (Relational Model & Algebra):</b> Relational Data Model, Integrity Constraints, Tuple Relational Calculus, Domain Relational Calculus, SQL DDL/DML/DCL.<br/>"
        "• <b>Module 3 (Normalization):</b> Functional Dependencies, Armstrong's Axioms, Normal Forms (1NF, 2NF, 3NF, BCNF, 4NF, 5NF), Lossless Join, Dependency Preservation.<br/>"
        "• <b>Module 4 (Transaction Processing):</b> ACID Properties, Concurrency Control, Two-Phase Locking (2PL), Timestamp Ordering, Deadlock detection and recovery.<br/>"
        "• <b>Module 5 (Storage & Indexing):</b> File Organization, RAID, B-Trees, B+ Tree Indexing, Hashing."
    )
    story.append(Paragraph(cs301_text, body_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Course Syllabus: CS305 — Machine Learning", h1_style))
    cs305_text = (
        "<b>Course Code:</b> CS305 | <b>Credits:</b> 4 Credits (L-T-P: 3-1-0) | <b>Semester:</b> Fifth Semester (Semester 5)<br/>"
        "<b>Course Type:</b> Professional Core | <b>Prerequisites:</b> MA202 (Probability and Statistics) and CS102 (Data Structures).<br/>"
        "<b>Syllabus Modules:</b><br/>"
        "• <b>Module 1 (Supervised Learning):</b> Linear Regression, Cost Functions, Gradient Descent, Logistic Regression, Multi-class Classification, Regularization (L1/L2 Lasso & Ridge).<br/>"
        "• <b>Module 2 (Tree-based & Non-Parametric):</b> Decision Trees (ID3, C4.5, CART), Information Gain, Random Forests, Gradient Boosted Trees (XGBoost), k-Nearest Neighbors (k-NN).<br/>"
        "• <b>Module 3 (Kernel Methods):</b> Support Vector Machines (SVM), Hyperplane margin maximization, Kernel trick (RBF, Polynomial kernels).<br/>"
        "• <b>Module 4 (Unsupervised Learning):</b> k-Means Clustering, Hierarchical Agglomerative Clustering, Principal Component Analysis (PCA), Dimensionality Reduction.<br/>"
        "• <b>Module 5 (Neural Networks Introduction):</b> Multilayer Perceptrons (MLP), Backpropagation algorithm, Activation functions (ReLU, Sigmoid, Softmax), Overfitting and Dropout."
    )
    story.append(Paragraph(cs305_text, body_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Course Syllabus: CS311 — Data Science Fundamentals (Elective)", h1_style))
    cs311_text = (
        "<b>Course Code:</b> CS311 | <b>Credits:</b> 3 Credits (L-T-P: 3-0-0) | <b>Semester:</b> Fifth Semester (Semester 5 Elective)<br/>"
        "<b>Course Type:</b> Professional Elective | <b>Prerequisites:</b> CS101 (Programming with C) or Python Programming Fundamentals.<br/>"
        "<b>Syllabus Modules:</b> Exploratory Data Analysis (EDA), NumPy, Pandas DataFrame operations, Data Cleaning, Matplotlib & Seaborn data visualization, Hypothesis Testing, Feature Engineering, Introduction to Big Data pipelines."
    )
    story.append(Paragraph(cs311_text, body_style))

    doc.build(story)
    print(f"Sample curriculum PDF generated at: {path}")


def generate_academic_regulations_pdf(output_path: str | Path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle2',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e293b"),
        alignment=1,
        spaceAfter=10
    )
    h1_style = ParagraphStyle(
        'H1_2',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body2',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155")
    )

    story = [
        Paragraph("University Academic Regulations & Grading Policy (R-2024)", title_style),
        Paragraph("Applicable to all Undergraduate B.Tech Programs", body_style),
        Spacer(1, 10),
        Paragraph("Section 1: Minimum Academic Credit Requirements", h1_style),
        Paragraph("Every undergraduate student must earn a minimum total of 160 credits to be eligible for the award of B.Tech Degree in Computer Science and Engineering. Out of these, a minimum of 20 credits must come from Humanities and Social Sciences (HSMC), and 24 credits from Basic Science Courses (BSC).", body_style),
        Spacer(1, 8),
        Paragraph("Section 2: Examination Evaluation Scheme", h1_style),
        Paragraph("Continuous Internal Assessment (CIA) accounts for 40% of the total course marks, consisting of two internal mid-term examinations (30 marks) and active assignment submissions (10 marks). The End Semester University Examination (ESE) carries 60% weightage.", body_style),
        Spacer(1, 8),
        Paragraph("Section 3: Grading Scale and Grade Point Average (GPA)", h1_style),
        Paragraph("The university uses a 10-point letter grading system: O (Outstanding, 10 points for marks >= 90%), A+ (Excellent, 9 points for marks 80-89%), A (Very Good, 8 points for marks 70-79%), B+ (Good, 7 points for marks 60-69%), B (Above Average, 6 points for marks 50-59%), C (Pass, 5 points for marks 40-49%), and F (Fail, 0 points for marks < 40%).", body_style),
    ]

    doc.build(story)
    print(f"Academic Regulations PDF generated at: {path}")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "B.Tech_CSE_Curriculum_2024-2028.pdf"
    generate_sample_curriculum_pdf(out)
    reg_out = Path(__file__).resolve().parent / "University_Academic_Regulations_2024.pdf"
    generate_academic_regulations_pdf(reg_out)
