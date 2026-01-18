# app.py
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
import os
import tempfile

from main import generate_song_artifacts

app = FastAPI()

def run_script(input_str: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        output_path = tmp.name
    return generate_song_artifacts(input_str, output_path)

@app.post("/run")
def run(input_str: str = Form(...)):
    output_path = run_script(input_str)
    return FileResponse(
        output_path,
        filename=os.path.basename(output_path),
        media_type="application/octet-stream",
    )
