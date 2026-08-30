# Sample Resume Extraction Results

This file maps each sample resume to its corresponding structured JSON output.
The examples below use valid JSON: email addresses and underscores do not need
Markdown escaping, and profile links are represented as plain URL strings.

## Sample 1: Arjun Mehta — Backend Engineer

**Resume:** [`arjun_mehta_backend_engineer.pdf`](./arjun_mehta_backend_engineer.pdf)

Run the extractor:

```bash
python -m resume_extractor.cli "arjun_mehta_backend_engineer.pdf"
```

Expected JSON:

```json
{
  "name": "Arjun Mehta",
  "email": "arjun.mehta@example.test",
  "phone": "+91 99887 66554",
  "skills": [
    "Git",
    "CI",
    "Java",
    "Python",
    "SQL",
    "Spring Boot",
    "REST APIs",
    "PostgreSQL",
    "Redis",
    "Kafka",
    "AWS",
    "Kubernetes",
    "Terraform",
    "Jenkins",
    "CI/CD",
    "CD"
  ],
  "education": [
    {
      "degree": "B.E. in Information Technology",
      "institution": "Greenfield College of Engineering"
    }
  ],
  "work_experience": [
    {
      "title": "Senior Backend Engineer",
      "company": "OrbitPay Technologies",
      "duration": "Mar 2022 - Present"
    },
    {
      "title": "Software Engineer",
      "company": "Northwind Digital",
      "duration": "Aug 2019 - Feb 2022"
    }
  ],
  "linkedin": "https://www.linkedin.com/in/arjunmehta",
  "github": "https://github.com/arjun-mehta"
}
```

## Sample 2: Nora Williams — Product Designer

**Resume:** [`nora_williams_product_designer.docx`](./nora_williams_product_designer.docx)

Run the extractor:

```bash
python -m resume_extractor.cli "nora_williams_product_designer.docx"
```

Expected JSON:

```json
{
  "name": "Nora Williams",
  "email": "nora.williams@example.test",
  "phone": "+1 (415) 555-0186",
  "skills": [
    "Figma",
    "User Research",
    "Wireframing",
    "Prototyping",
    "Design Systems",
    "HTML",
    "CSS",
    "JavaScript",
    "Agile",
    "Jira"
  ],
  "education": [
    {
      "degree": "Bachelor of Design in Interaction Design",
      "institution": "Northshore Institute of Design"
    }
  ],
  "work_experience": [
    {
      "title": "Senior Product Designer",
      "company": "Brightside Systems",
      "duration": "Apr 2023 - Present"
    },
    {
      "title": "Product Designer",
      "company": "Harbor Labs",
      "duration": "Jul 2020 - Mar 2023"
    }
  ],
  "linkedin": "https://linkedin.com/in/nora-williams",
  "github": "https://github.com/norawilliams"
}
```

