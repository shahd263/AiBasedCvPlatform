from pydantic import BaseModel
from typing import List, Optional, Dict


class HeaderSchema(BaseModel):
    fullName: Optional[str] = None
    jobTitle: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    urls: Optional[List[str]] = None  # replaces LinkedIn & GitHub


class ExperienceSchema(BaseModel):
    jobTitle: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    dates: Optional[str] = None  # single string for date range
    responsibilities: Optional[List[str]] = None


class EducationSchema(BaseModel):
    degree: Optional[str] = None
    major: Optional[str] = None
    university: Optional[str] = None
    graduationYear: Optional[int] = None
    gpa: Optional[str] = None


class ProjectSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    dates: Optional[str] = None  # single string for project timeline (e.g. "Jan 2023 – Dec 2024")
    url: Optional[str] = None  # repo, demo, or project page


class CertificationSchema(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    year: Optional[int] = None


class LanguageSchema(BaseModel):
    language: Optional[str] = None
    proficiency: Optional[str] = None


class GeneratedResumeSchema(BaseModel):
    header: Optional[HeaderSchema] = None
    professionalSummary: Optional[str] = None
    experience: Optional[List[ExperienceSchema]] = None
    education: Optional[List[EducationSchema]] = None
    skills: Optional[Dict[str, List[str]]] = None
    projects: Optional[List[ProjectSchema]] = None
    certifications: Optional[List[CertificationSchema]] = None
    languages: Optional[List[LanguageSchema]] = None

class CvGenerateResponse(BaseModel):
    template_id: int
    generate_cv_response: GeneratedResumeSchema