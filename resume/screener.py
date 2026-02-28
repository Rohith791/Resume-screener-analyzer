# resume/screener.py
from resume.parser import parse_resume
from resume.ai_client import client
from config import MODEL_NAME
import json
import time
import re
import os

CHUNK_SIZE = 5   # number of resumes per API call
RETRY_LIMIT = 2  # retry API call if empty/invalid response
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def screen_resumes_chunked(files, job_description):
    """
    Process resumes in batches of CHUNK_SIZE per API call.
    Returns a list of dictionaries:
    [{filename, match_score, matching_skills, missing_skills, suggestions}, ...]
    """

    resumes_text = []

    # Save uploaded files and parse text
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        text = parse_resume(file_path)
        resumes_text.append({"filename": file.filename, "text": text})

    results = []

    # Process in chunks
    for i in range(0, len(resumes_text), CHUNK_SIZE):
        chunk = resumes_text[i:i + CHUNK_SIZE]

        prompt = (
            "You are an expert HR AI. I will provide a job description and multiple resumes. "
            "Analyze each resume for match with the job description. For each resume, return:\n"
            "- MATCH_SCORE (0-100)\n"
            "- MATCHING_SKILLS\n"
            "- MISSING_SKILLS\n"
            "- SUGGESTIONS\n"
            "Return results as a JSON array:\n"
            "[{filename, match_score, matching_skills, missing_skills, suggestions}]\n\n"
            f"Job Description:\n{job_description}\n\nResumes:\n{chunk}"
        )

        # Retry loop
        for attempt in range(RETRY_LIMIT + 1):
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.choices[0].message.content.strip()

            if not content:
                print(f"Warning: Empty response for chunk {i//CHUNK_SIZE + 1}, attempt {attempt+1}")
                time.sleep(1)
                continue

            # Clean up AI output to isolate JSON
            try:
                # Extract text between first [ and last ]
                if "[" in content and "]" in content:
                    json_text = content[content.index("["): content.rindex("]")+1]
                    # Remove trailing commas before ]
                    json_text = re.sub(r",\s*]", "]", json_text)
                    # Replace smart quotes
                    json_text = json_text.replace("“", '"').replace("”", '"')
                    # Parse JSON
                    chunk_result = json.loads(json_text)
                    if isinstance(chunk_result, list):
                        results.extend(chunk_result)
                        break  # exit retry loop
                    else:
                        print(f"Warning: Response is not a JSON array:\n{json_text}")
                else:
                    print(f"Warning: No JSON array found in AI response:\n{content}")
            except json.JSONDecodeError:
                print(f"Warning: Invalid JSON for chunk {i//CHUNK_SIZE + 1}, attempt {attempt+1}:\n{content}")
                time.sleep(1)
        else:
            print(f"Error: Failed to parse JSON for chunk {i//CHUNK_SIZE + 1}. Skipping this chunk.")

    # Sort results by match_score descending
    results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return results