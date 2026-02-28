from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os

from resume.screener import screen_resumes_chunked

from resume.parser import parse_resume
from resume.analyzer import analyze_resume
from resume.matcher import match_resume_to_job

app = FastAPI(title="Smart Resume Analyzer")

app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()


@app.post("/analyze")
async def analyze(file: UploadFile = File(...),
                  job_description: str = Form(...)):

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_text = parse_resume(file_path)

    analysis = analyze_resume(resume_text)
    match = match_resume_to_job(resume_text, job_description)

    return {
        "analysis": analysis,
        "match_result": match
    }

@app.get("/screener", response_class=HTMLResponse)
def screener_page():
    try:
        with open("templates/screener.html", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return HTMLResponse(
            content=f"<h2>Error loading page</h2><p>{str(e)}</p>",
            status_code=500
        )
    
@app.post("/screener")
async def resume_screener(files: list[UploadFile] = None, job_description: str = Form(...)):
    if not files or len(files) == 0:
        return {"error": "Please upload at least one resume"}

    results = screen_resumes_chunked(files, job_description)
    return {"results": results}