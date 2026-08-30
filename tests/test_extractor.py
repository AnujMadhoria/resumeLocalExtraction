import tempfile
import unittest
from pathlib import Path

from resume_extractor import extract_resume, extract_text
from resume_extractor.parsers import ResumeParseError


SAMPLE = """JOHN DOE
Software Engineer
john.doe@email.com | +91 98765 43210
linkedin.com/in/johndoe | github.com/johndoe

SKILLS
Python, SQL, Machine Learning, FastAPI, Docker

EDUCATION
B.Tech in Computer Science | ABC University

WORK EXPERIENCE
Software Engineer | Example Technologies | Jan 2022 - Present
Built reliable Python services.
"""


class TextExtractionTests(unittest.TestCase):
    def test_all_supported_fields(self):
        result = extract_text(SAMPLE)

        self.assertEqual(result["name"], "John Doe")
        self.assertEqual(result["email"], "john.doe@email.com")
        self.assertEqual(result["phone"], "+91 98765 43210")
        self.assertEqual(
            result["skills"], ["Python", "SQL", "Machine Learning", "FastAPI", "Docker"]
        )
        self.assertEqual(result["linkedin"], "https://linkedin.com/in/johndoe")
        self.assertEqual(result["github"], "https://github.com/johndoe")
        self.assertEqual(result["education"][0]["institution"], "ABC University")
        self.assertEqual(result["work_experience"][0]["company"], "Example Technologies")
        self.assertEqual(result["work_experience"][0]["duration"], "Jan 2022 - Present")

    def test_absent_fields_are_stable(self):
        result = extract_text("Jane Smith\njane@example.org\nSkills\nRust")
        self.assertIsNone(result["phone"])
        self.assertEqual(result["education"], [])
        self.assertEqual(result["work_experience"], [])
        self.assertIsNone(result["linkedin"])

    def test_dates_are_not_phone_numbers(self):
        result = extract_text("Jane Smith\njane@example.org\n2019 - 2023\nSkills\nJava")
        self.assertIsNone(result["phone"])


class FileExtractionTests(unittest.TestCase):
    def test_docx_round_trip(self):
        from docx import Document

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resume.docx"
            document = Document()
            for line in SAMPLE.splitlines():
                document.add_paragraph(line)
            document.save(path)
            result = extract_resume(path)

        self.assertEqual(result["name"], "John Doe")
        self.assertIn("Python", result["skills"])

    def test_pdf_round_trip(self):
        from reportlab.pdfgen.canvas import Canvas

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resume.pdf"
            canvas = Canvas(str(path))
            y = 800
            for line in SAMPLE.splitlines():
                canvas.drawString(60, y, line)
                y -= 18
            canvas.save()
            result = extract_resume(path)

        self.assertEqual(result["email"], "john.doe@email.com")
        self.assertEqual(result["github"], "https://github.com/johndoe")

    def test_rejects_unsupported_type(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resume.txt"
            path.write_text(SAMPLE, encoding="utf-8")
            with self.assertRaises(ResumeParseError):
                extract_resume(path)


if __name__ == "__main__":
    unittest.main()

