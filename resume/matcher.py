from resume.ai_client import client
from config import MODEL_NAME

def match_resume_to_job(resume_text, job_description):

    prompt = f"""
Compare resume and job description.

Return:

MATCH_SCORE: (0-100)

MATCHING_SKILLS:
...

MISSING_SKILLS:
...

SUGGESTIONS:
...

Resume:
{resume_text}

Job Description:
{job_description}

Note: Avoid using special characters. Please provide a neat, clean, and simple response.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content