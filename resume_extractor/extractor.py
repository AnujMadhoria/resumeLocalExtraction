"""Deterministic, non-LLM resume information extraction."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .parsers import parse_file


EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.I)
PHONE_RE = re.compile(
    r"(?<!\w)(?:\+\d{1,3}[\s.()-]*)?(?:\(?\d{2,5}\)?[\s.()-]*)?"
    r"\d(?:[\s.()-]*\d){7,12}(?!\w)"
)

SECTION_ALIASES = {
    "skills": {"skills", "technical skills", "core competencies", "competencies", "technologies", "tech stack"},
    "education": {"education", "academic background", "academic qualifications", "qualifications"},
    "experience": {"experience", "work experience", "professional experience", "employment history", "career history"},
    "projects": {"projects", "personal projects", "academic projects"},
    "summary": {"summary", "profile", "professional summary", "objective", "career objective", "about me"},
    "certifications": {"certifications", "certificates", "licenses & certifications", "licenses and certifications"},
    "awards": {"awards", "achievements", "honors", "accomplishments"},
    "languages": {"languages", "language proficiency"},
    "interests": {"interests", "hobbies"},
}

SECTION_LOOKUP = {
    alias: canonical for canonical, aliases in SECTION_ALIASES.items() for alias in aliases
}

# Canonical skill -> spelling variants. This is deliberately data-driven so the
# project can be extended without changing extraction code.
SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "Python": ("python",),
    "Java": ("java",),
    "JavaScript": ("javascript", "java script"),
    "TypeScript": ("typescript", "type script"),
    "C": ("c language",),
    "C++": ("c++", "cpp"),
    "C#": ("c#", "c sharp"),
    "Go": ("golang", "go language"),
    "Rust": ("rust",),
    "PHP": ("php",),
    "Ruby": ("ruby",),
    "Kotlin": ("kotlin",),
    "Swift": ("swift",),
    "R": ("r programming", "r language"),
    "SQL": ("sql",),
    "HTML": ("html", "html5"),
    "CSS": ("css", "css3"),
    "React": ("react", "react.js", "reactjs"),
    "Angular": ("angular", "angularjs"),
    "Vue.js": ("vue", "vue.js", "vuejs"),
    "Node.js": ("node", "node.js", "nodejs"),
    "Express.js": ("express", "express.js", "expressjs"),
    "Django": ("django",),
    "Flask": ("flask",),
    "FastAPI": ("fastapi",),
    "Spring Boot": ("spring boot",),
    ".NET": (".net", "dotnet", "asp.net"),
    "REST APIs": ("rest api", "restful api", "rest apis", "restful services"),
    "GraphQL": ("graphql",),
    "MySQL": ("mysql",),
    "PostgreSQL": ("postgresql", "postgres"),
    "SQLite": ("sqlite",),
    "Oracle": ("oracle database", "oracle db"),
    "SQL Server": ("sql server", "mssql"),
    "MongoDB": ("mongodb", "mongo db"),
    "Redis": ("redis",),
    "Elasticsearch": ("elasticsearch", "elastic search"),
    "AWS": ("aws", "amazon web services"),
    "Azure": ("azure", "microsoft azure"),
    "Google Cloud": ("gcp", "google cloud", "google cloud platform"),
    "Docker": ("docker",),
    "Kubernetes": ("kubernetes", "k8s"),
    "Terraform": ("terraform",),
    "Jenkins": ("jenkins",),
    "GitHub Actions": ("github actions",),
    "CI/CD": ("ci/cd", "continuous integration", "continuous deployment"),
    "Git": ("git",),
    "Linux": ("linux",),
    "Machine Learning": ("machine learning", "ml"),
    "Deep Learning": ("deep learning",),
    "Natural Language Processing": ("natural language processing", "nlp"),
    "Computer Vision": ("computer vision",),
    "Data Science": ("data science",),
    "Data Analysis": ("data analysis", "data analytics"),
    "Pandas": ("pandas",),
    "NumPy": ("numpy",),
    "scikit-learn": ("scikit-learn", "sklearn"),
    "TensorFlow": ("tensorflow",),
    "PyTorch": ("pytorch",),
    "Keras": ("keras",),
    "OpenCV": ("opencv",),
    "Power BI": ("power bi", "powerbi"),
    "Tableau": ("tableau",),
    "Excel": ("microsoft excel", "ms excel", "excel"),
    "Spark": ("apache spark", "pyspark"),
    "Hadoop": ("hadoop",),
    "Kafka": ("apache kafka", "kafka"),
    "Airflow": ("apache airflow", "airflow"),
    "Figma": ("figma",),
    "Jira": ("jira",),
    "Agile": ("agile",),
    "Scrum": ("scrum",),
    "Selenium": ("selenium",),
    "Cypress": ("cypress",),
    "Playwright": ("playwright",),
    "Postman": ("postman",),
    "Unit Testing": ("unit testing", "unit tests"),
}

DEGREE_RE = re.compile(
    r"\b(?:b\.?\s?tech|m\.?\s?tech|b\.?e\.?|m\.?e\.?|b\.?sc|m\.?sc|bca|mca|"
    r"bba|mba|ph\.?d|doctorate|bachelor(?:'s)?|master(?:'s)?|diploma|associate(?:'s)?)\b",
    re.I,
)
INSTITUTION_RE = re.compile(
    r"\b(?:university|college|institute|school|academy|polytechnic|iit|nit)\b", re.I
)
DATE_RANGE_RE = re.compile(
    r"\b(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+)?"
    r"(?:19|20)\d{2}\s*(?:-|–|—|to)\s*"
    r"(?:(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+)?"
    r"(?:19|20)\d{2}|present|current|now)\b",
    re.I,
)


def extract_resume(path: str | Path) -> dict[str, Any]:
    """Extract structured fields from a PDF or DOCX resume."""
    return extract_text(parse_file(path))


def extract_text(text: str) -> dict[str, Any]:
    """Extract structured fields from already-parsed resume text."""
    normalized = _normalize_text(text)
    lines = [line.strip(" \t|•·▪◦-–—") for line in normalized.splitlines() if line.strip()]
    sections = _split_sections(lines)

    return {
        "name": _extract_name(lines),
        "email": _extract_email(normalized),
        "phone": _extract_phone(normalized),
        "skills": _extract_skills(normalized, sections),
        "education": _extract_education(sections.get("education", [])),
        "work_experience": _extract_experience(sections.get("experience", [])),
        "linkedin": _extract_profile(normalized, "linkedin"),
        "github": _extract_profile(normalized, "github"),
    }


def _normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Repair common PDF extraction artefact: "john @ email.com".
    text = re.sub(r"(?<=\w)\s+@\s+(?=\w)", "@", text)
    return text.strip()


def _heading(line: str) -> str | None:
    clean = re.sub(r"[^a-z& ]", "", line.lower()).strip()
    return SECTION_LOOKUP.get(clean) if len(clean.split()) <= 4 else None


def _split_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"header": []}
    current = "header"
    for line in lines:
        heading = _heading(line)
        if heading:
            current = heading
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(line)
    return sections


def _extract_email(text: str) -> str | None:
    match = EMAIL_RE.search(text)
    return match.group(0).rstrip(".,;:").lower() if match else None


def _extract_phone(text: str) -> str | None:
    candidates: list[tuple[int, str]] = []
    for match in PHONE_RE.finditer(text):
        raw = match.group(0).strip(" .,;-—")
        digits = re.sub(r"\D", "", raw)
        if not 10 <= len(digits) <= 15:
            continue
        # Exclude date ranges and long year-like numeric runs.
        if DATE_RANGE_RE.fullmatch(raw) or re.fullmatch(r"(?:19|20)\d{2}\D+(?:19|20)\d{2}", raw):
            continue
        context = text[max(0, match.start() - 12) : match.start()].lower()
        score = (3 if re.search(r"(?:phone|mobile|tel|contact)\D*$", context) else 0)
        score += 2 if raw.startswith("+") else 0
        score += 1 if len(digits) in (10, 12) else 0
        candidates.append((score, raw))
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[0])[1]


def _extract_profile(text: str, site: str) -> str | None:
    domain = "linkedin.com/in/" if site == "linkedin" else "github.com/"
    pattern = re.compile(
        rf"(?:https?://)?(?:www\.)?{re.escape(domain)}[A-Za-z0-9_.%-]+/?", re.I
    )
    match = pattern.search(text)
    if not match:
        return None
    url = match.group(0).rstrip("/.,;:)")
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    return url


def _extract_name(lines: list[str]) -> str | None:
    # Prefer an explicit label when present.
    for line in lines[:12]:
        match = re.match(r"(?:full\s+)?name\s*[:|-]\s*(.+)$", line, re.I)
        if match and _is_name(match.group(1)):
            return _title_name(match.group(1))

    for line in lines[:12]:
        if _is_name(line):
            return _title_name(line)

    # Mononyms are uncommon but valid. Keep this as a fallback so a single-word
    # name is not mistaken for a section heading or job title.
    for line in lines[:5]:
        if (
            re.fullmatch(r"[A-Za-z][A-Za-z'.-]{1,39}", line)
            and not _heading(line)
            and line.lower() not in {"resume", "cv", "developer", "engineer", "manager"}
        ):
            return _title_name(line)
    return None


def _is_name(value: str) -> bool:
    value = value.strip()
    words = value.split()
    if not 2 <= len(words) <= 5 or len(value) > 60:
        return False
    lower = value.lower()
    if _heading(value) or EMAIL_RE.search(value) or "http" in lower or "www." in lower:
        return False
    if re.search(r"\d|[@|:/]", value):
        return False
    blocked = {
        "resume", "curriculum", "vitae", "developer", "engineer", "manager",
        "analyst", "consultant", "designer", "scientist", "specialist", "intern",
        "phone", "email", "address", "linkedin", "github", "professional",
    }
    tokens = [re.sub(r"[^a-z'-]", "", word.lower()) for word in words]
    if any(token in blocked for token in tokens):
        return False
    return all(re.fullmatch(r"[A-Za-z][A-Za-z'.-]*", word) for word in words)


def _title_name(name: str) -> str:
    # Preserve already mixed-case names; improve ALL CAPS without mangling McFoo.
    return name.title() if name == name.upper() else name.strip()


def _contains_alias(text_lower: str, alias: str) -> bool:
    return bool(re.search(rf"(?<![\w+#.]){re.escape(alias)}(?![\w+#.])", text_lower))


def _extract_skills(text: str, sections: dict[str, list[str]]) -> list[str]:
    # Searching the whole document catches skills mentioned in experience, while
    # the section is also parsed for valid skills not yet present in the dictionary.
    lower = text.lower()
    found: list[tuple[int, str]] = []
    for canonical, aliases in SKILL_ALIASES.items():
        positions = [lower.find(alias) for alias in aliases if _contains_alias(lower, alias)]
        if positions:
            found.append((min(pos for pos in positions if pos >= 0), canonical))

    existing = {skill.lower() for _, skill in found}
    skill_lines = sections.get("skills", [])
    skill_text = " | ".join(skill_lines)
    for token in re.split(r"[,|;/•·▪◦]|\s{2,}", skill_text):
        token = re.sub(r"^(?:languages?|frameworks?|tools?|databases?|cloud|other)\s*:\s*", "", token.strip(), flags=re.I)
        token = token.strip(" .:-")
        if _valid_unknown_skill(token) and token.lower() not in existing:
            found.append((lower.find(token.lower()) if token.lower() in lower else len(lower), token))
            existing.add(token.lower())

    return [skill for _, skill in sorted(found, key=lambda pair: pair[0])]


def _valid_unknown_skill(token: str) -> bool:
    if not token or len(token) > 35 or len(token.split()) > 4:
        return False
    if re.search(r"\b(?:experience|proficient|knowledge|familiar|years?|worked|using|and)\b", token, re.I):
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 .+#/-]*", token))


def _extract_education(lines: list[str]) -> list[dict[str, str | None]]:
    records: list[dict[str, str | None]] = []
    pending_institution: str | None = None
    for index, line in enumerate(lines):
        degree_match = DEGREE_RE.search(line)
        institution_match = INSTITUTION_RE.search(line)
        if degree_match:
            degree = re.sub(r"\s{2,}", " ", line).strip(" ,|-")
            # If a pipe or comma separates degree and institution, retain each cleanly.
            parts = [part.strip() for part in re.split(r"\s*[|]\s*", line) if part.strip()]
            degree_part = next((part for part in parts if DEGREE_RE.search(part)), degree)
            institution = next((part for part in parts if INSTITUTION_RE.search(part)), None)
            if not institution and index + 1 < len(lines) and INSTITUTION_RE.search(lines[index + 1]):
                institution = lines[index + 1]
            if not institution:
                institution = pending_institution
            records.append({"degree": degree_part, "institution": institution})
            pending_institution = None
        elif institution_match:
            pending_institution = line

    # Some resumes list institution before degree. Attach it when unambiguous.
    return _dedupe_records(records, ("degree", "institution"))


def _extract_experience(lines: list[str]) -> list[dict[str, str | None]]:
    if not lines:
        return []
    records: list[dict[str, str | None]] = []
    title_words = re.compile(
        r"\b(?:engineer|developer|manager|analyst|consultant|designer|scientist|"
        r"specialist|intern|architect|administrator|lead|director|associate|officer)\b",
        re.I,
    )

    for index, line in enumerate(lines):
        if not title_words.search(line):
            continue
        duration_match = DATE_RANGE_RE.search(line)
        duration = duration_match.group(0) if duration_match else None
        title = DATE_RANGE_RE.sub("", line).strip(" ,|-")
        company: str | None = None

        parts = [part.strip() for part in re.split(r"\s*[|@]\s*", title) if part.strip()]
        if len(parts) >= 2:
            title, company = parts[0], parts[1]
        elif index + 1 < len(lines):
            next_line = lines[index + 1]
            if not title_words.search(next_line) and not next_line.startswith(("•", "-")):
                if len(next_line) <= 100:
                    company = DATE_RANGE_RE.sub("", next_line).strip(" ,|-") or None
                if duration is None:
                    next_duration = DATE_RANGE_RE.search(next_line)
                    duration = next_duration.group(0) if next_duration else None

        records.append({"title": title, "company": company, "duration": duration})

    return _dedupe_records(records, ("title", "company", "duration"))


def _dedupe_records(
    records: list[dict[str, Any]], keys: tuple[str, ...]
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for record in records:
        identity = tuple(record.get(key) for key in keys)
        if identity not in seen:
            seen.add(identity)
            output.append(record)
    return output
