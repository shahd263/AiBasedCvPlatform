from pydantic import BaseModel
from typing import List, Optional


class ContactInfoSchema(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    urls: Optional[List[str]] = None  # List of any URLs


class ExperienceSchema(BaseModel):
    jobTitle: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
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
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    url: Optional[str] = None  # repo, demo, or project page


class CertificationSchema(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    year: Optional[int] = None


class LanguageSchema(BaseModel):
    language: Optional[str] = None
    proficiency: Optional[str] = None


class CandidateDataSchema(BaseModel):
    fullName: Optional[str] = None
    jobTitle: Optional[str] = None
    contactInfo: Optional[ContactInfoSchema] = None
    summary: Optional[str] = None
    experience: Optional[List[ExperienceSchema]] = None
    education: Optional[List[EducationSchema]] = None
    technicalSkills: Optional[List[str]] = None
    softSkills: Optional[List[str]] = None
    projects: Optional[List[ProjectSchema]] = None
    certifications: Optional[List[CertificationSchema]] = None
    languages: Optional[List[LanguageSchema]] = None


class CvGenerateRequest(BaseModel):
    template_id: int
    candidate_data: CandidateDataSchema

class CoverLetterRequest(BaseModel):
    cvId: int
    job_description: str

class AutofillApplicationRequest(BaseModel):
    candidate_data: CandidateDataSchema
    job_url: str
