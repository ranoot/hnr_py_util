# app.py
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import html
import tempfile

from main import generate_song_artifacts

app = FastAPI()

def run_script(input_str: str, song_num: int) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        output_path = tmp.name
    return generate_song_artifacts(input_str, output_path, song_num)

@app.get("/", response_class=HTMLResponse)
def form():
    return """
    <html>
      <head>
        <title>RTTTL Generator</title>
      </head>
      <body>
        <h1>RTTTL Generator</h1>
        <form method="post">
          <label>RTTTL String</label><br/>
          <textarea name="rtttl_str" rows="6" cols="80"></textarea><br/><br/>
          <label>Song Number</label><br/>
          <input type="number" name="song_num" value="2"/><br/><br/>
          <button type="submit">Generate</button>
        </form>
      </body>
    </html>
    """

@app.post("/", response_class=HTMLResponse)
def run(rtttl_str: str = Form(...), song_num: int = Form(...)):
    output = run_script(rtttl_str, song_num)
    escaped = html.escape(output)
    return f"""
    <html>
      <head>
        <title>RTTTL Output</title>
      </head>
      <body>
        <h1>Output</h1>
        <pre>{escaped}</pre>
        <a href="/">Back</a>
      </body>
    </html>
    """
