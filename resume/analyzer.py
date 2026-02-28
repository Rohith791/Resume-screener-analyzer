from resume.ai_client import client
from config import MODEL_NAME

def analyze_resume(resume_text):

    prompt = f"""
Analyze this resume and extract:

1. Key Skills
2. Experience Summary
3. Strengths
4. Weaknesses

Resume:
{resume_text}

Note: Avoid using special characters. Please provide a neat, clean, and simple response.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content