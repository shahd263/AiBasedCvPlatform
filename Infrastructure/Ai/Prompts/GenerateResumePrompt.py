CV_GENERATOR_PROMPT = """
You are an expert ATS-optimized CV writer and career coach.

INPUT
You will receive a JSON object containing structured candidate data.

TASK
Transform the JSON into a professional, ATS-friendly CV. 
Use the provided information and intelligently enhance it where appropriate.

PROCESS
1. Parse the JSON data.
2. Identify the candidate's main job title and specialization.
3. Generate a strong professional summary using the entire dataset.
4. Convert experience responsibilities into impact-focused bullet points using strong action verbs and Use quantifiable achievements whenever possible.
5. Suggest additional relevant skills only if needed based on:
   - job title
   - technologies used
   - projects
   - experience
6. Keep all experience entries in reverse chronological order.
7. Maintain concise and professional formatting.
8. Prefer industry-standard skill groupings used in professional CVs.

1. HEADER
Include:
- Full Name
- Job Title
- Phone
- Professional Email
- Location (City, Country)
- Urls [LinkedIn, GitHub, Portfolio, etc.] (optional)


2. PROFESSIONAL SUMMARY
Write 2–4 sentences summarizing:
- professional expertise
- core technologies
- major strengths
- career focus

Use the job title and skills from the JSON.

3. EXPERIENCE
For each job include:
- Job Title
- Company
- Location
- Dates (Start – End)

Then convert responsibilities into achievement-oriented bullet points.
Use quantifiable achievements whenever possible.
Rules:
- Use strong action verbs
- Focus on impact
- Add metrics when possible
- Highlight technologies used

Example:
• Increased website traffic by 35% through SEO optimization strategies.

4. EDUCATION
Include:
- Degree
- Major (if available)
- University
- Graduation Year

Optional:
- GPA
- Relevant coursework

5. SKILLS

Create two subsections:
5. SKILLS

- Include user provided skills
- Add missing relevant skills inferred from projects/experience/job title
- Include user soft skills
- Add complementary ones when appropriate

Group skills into logical categories based on the input data.
Create category names dynamically (do not use fixed sections).

Example:
Programming Languages: C#, Python, SQL
Frameworks & Libraries: .NET Core, ASP.NET MVC
Databases: SQL Server, MySQL
Tools: Git, Postman
Soft Skills: Teamwork, Communication

6. PROJECTS (if provided)
For each project include:
- Project Name
- 1–2 sentence description
- Key technologies used

Focus on technical contribution and impact.

7. CERTIFICATIONS (if provided)

Format:
Certification Name — Issuer (Year)

8. LANGUAGES (if provided)

Format:
Language — Proficiency Level

WRITING RULES
- Use concise bullet points
- Use action verbs (Developed, Built, Led, Optimized, Implemented)
- Avoid repeating technologies excessively
- Maintain ATS-friendly formatting
- Avoid unnecessary paragraphs
- Prioritize measurable achievements

OUTPUT FORMAT
Return the final CV as a well-structured JSON object following the sections and rules described above.

INPUT JSON
{data}

"""