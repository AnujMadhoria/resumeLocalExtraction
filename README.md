# Resume Information Extraction System

This application reads a resume in **PDF** or **DOCX** format and returns the
extracted information as structured JSON. All processing happens locally using
regular expressions and rule-based parsing. Resume content is never sent to an
LLM, Generative AI service, or external API.

## Information extracted

- Full name
- Email address
- Phone number
- Skills
- Education
- Work experience
- LinkedIn profile
- GitHub profile

## Requirements

- Python 3.10 or newer
- A text-based PDF or DOCX resume

Check that Python is installed:

```bash
python --version
```

On Windows, use `py --version` if the `python` command is unavailable.

## Setup

### Windows (PowerShell)

Open PowerShell in the project directory and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run the following command once in the same
terminal and then activate the environment again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### macOS or Linux

Open a terminal in the project directory and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

When the environment is active, the terminal prompt normally begins with
`(.venv)`.

## Run from the command line

Place a resume anywhere on your computer and pass its path to the program.

### Print the result in the terminal

```bash
python -m resume_extractor.cli "path/to/resume.pdf"
```

DOCX files work the same way:

```bash
python -m resume_extractor.cli "path/to/resume.docx"
```

Use quotation marks when a path contains spaces. For example, on Windows:

```powershell
python -m resume_extractor.cli "C:\Users\YourName\Documents\My Resume.pdf"
```

### Save the result to a JSON file

```bash
python -m resume_extractor.cli "path/to/resume.pdf" --output result.json
```

The generated `result.json` will resemble:

```json
{
  "name": "John Doe",
  "email": "john.doe@email.com",
  "phone": "+91 98765 43210",
  "skills": [
    "Python",
    "SQL",
    "Machine Learning"
  ],
  "education": [
    {
      "degree": "B.Tech in Computer Science",
      "institution": "ABC University"
    }
  ],
  "work_experience": [
    {
      "title": "Software Engineer",
      "company": "Example Technologies",
      "duration": "Jan 2022 - Present"
    }
  ],
  "linkedin": "https://linkedin.com/in/johndoe",
  "github": "https://github.com/johndoe"
}
```

Fields that cannot be found are returned as `null` or an empty list.

## Run the web API

The API provides a browser-based interface where a PDF or DOCX file can be
uploaded.

### 1. Start the server

Make sure the virtual environment is active, then run:

```bash
uvicorn resume_extractor.api:app --reload
```

The terminal should report that the server is running at
`http://127.0.0.1:8000`.

### 2. Upload a resume

Open the following address in a browser:

```text
http://127.0.0.1:8000/docs
```

Then:

1. Expand `POST /extract`.
2. Select **Try it out**.
3. Choose a PDF or DOCX resume.
4. Select **Execute**.
5. Read the extracted JSON in the response section.

The API accepts files up to 10 MB. Its health endpoint is available at
`http://127.0.0.1:8000/health`.

### Optional: upload with curl

```bash
curl -X POST "http://127.0.0.1:8000/extract" \
  -F "file=@path/to/resume.pdf"
```

On Windows PowerShell, use `curl.exe` instead of `curl` if PowerShell maps
`curl` to another command.

Stop the API by pressing `Ctrl+C` in the terminal where it is running.

## Use from Python code

```python
from resume_extractor import extract_resume

result = extract_resume("resume.docx")
print(result)
print(result["skills"])
```

## Run the tests

Install the development dependencies and execute the test suite:

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

The tests cover PDF and DOCX parsing, field extraction, missing fields, and
unsupported file types.

## Common problems

### `python` is not recognized

Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/).
On Windows, select **Add Python to PATH** during installation. You can also try
using `py` instead of `python`.

### `No module named ...`

Activate the virtual environment and install the dependencies again:

```bash
pip install -r requirements.txt
```

### No text found in a PDF

The PDF is probably a scanned image rather than a text document. Run it through
an OCR tool first, save the searchable PDF, and try again.

### Some fields are missing

Rule-based extraction works best with conventional headings such as `Skills`,
`Education`, and `Work Experience`. Unavailable values are intentionally
returned as `null` or `[]` rather than guessed.

## Project structure

```text
resume_extractor/
├── __init__.py     Public Python interface
├── api.py          FastAPI upload endpoint
├── cli.py          Command-line interface
├── extractor.py    Rule-based field extraction
└── parsers.py      PDF and DOCX text parsing
tests/
└── test_extractor.py
```

To add more recognized technologies, extend `SKILL_ALIASES` in
`resume_extractor/extractor.py`.
