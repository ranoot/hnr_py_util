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
        <style>
          :root {
            --bg-top: #f4f1ec;
            --bg-bottom: #d7d2c6;
            --card: #ffffff;
            --ink: #1f1f1f;
            --accent: #d96c3b;
            --accent-dark: #b4552d;
            --muted: #6a6258;
            --ring: rgba(217, 108, 59, 0.25);
          }

          * {
            box-sizing: border-box;
          }

          body {
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 32px;
            font-family: "Space Grotesk", "Segoe UI", sans-serif;
            color: var(--ink);
            background:
              radial-gradient(800px 400px at 20% 20%, rgba(255, 255, 255, 0.7), transparent 60%),
              radial-gradient(800px 400px at 90% 10%, rgba(217, 108, 59, 0.15), transparent 50%),
              linear-gradient(160deg, var(--bg-top), var(--bg-bottom));
          }

          .card {
            width: min(900px, 95vw);
            background: var(--card);
            border-radius: 18px;
            padding: 36px;
            box-shadow:
              0 30px 60px rgba(31, 31, 31, 0.12),
              0 8px 16px rgba(31, 31, 31, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.06);
          }

          h1 {
            font-size: clamp(2rem, 3vw, 2.75rem);
            letter-spacing: -0.02em;
            margin: 0 0 12px;
          }

          p {
            margin: 0 0 24px;
            color: var(--muted);
            font-size: 1rem;
          }

          label {
            font-weight: 600;
            display: block;
            margin-bottom: 8px;
          }

          textarea,
          input[type="number"] {
            width: 100%;
            border: 1px solid rgba(0, 0, 0, 0.12);
            border-radius: 12px;
            padding: 12px 14px;
            font-size: 1rem;
            font-family: "JetBrains Mono", "Cascadia Mono", "Courier New", monospace;
            background: #fbfaf8;
            color: var(--ink);
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.08);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
          }

          textarea {
            min-height: 160px;
            resize: vertical;
          }

          textarea:focus,
          input[type="number"]:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 4px var(--ring);
          }

          .row {
            display: grid;
            grid-template-columns: 1fr 200px;
            gap: 16px;
            margin-bottom: 18px;
          }

          .actions {
            display: flex;
            justify-content: flex-end;
          }

          button {
            background: linear-gradient(135deg, var(--accent), var(--accent-dark));
            color: white;
            border: none;
            border-radius: 999px;
            padding: 12px 28px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow:
              0 10px 20px rgba(217, 108, 59, 0.25),
              inset 0 1px 0 rgba(255, 255, 255, 0.4);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
          }

          button:hover {
            transform: translateY(-1px);
            box-shadow:
              0 14px 28px rgba(217, 108, 59, 0.3),
              inset 0 1px 0 rgba(255, 255, 255, 0.5);
          }

          @media (max-width: 720px) {
            .row {
              grid-template-columns: 1fr;
            }

            .card {
              padding: 24px;
            }
          }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>RTTTL Generator</h1>
          <p>Convert RTTTL strings into arrays for your game audio pipeline.</p>
          <form method="post">
            <label>RTTTL String</label>
            <textarea name="rtttl_str" placeholder="Cantina:d=4, o=5, b=250:8a, 8p, ..."></textarea>
            <div class="row">
              <div>
                <label>Song Number</label>
                <input type="number" name="song_num" value="2" min="0"/>
              </div>
            </div>
            <div class="actions">
              <button type="submit">Generate</button>
            </div>
          </form>
        </div>
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
        <style>
          :root {{
            --bg-top: #f4f1ec;
            --bg-bottom: #d7d2c6;
            --card: #ffffff;
            --ink: #1f1f1f;
            --accent: #d96c3b;
            --accent-dark: #b4552d;
            --muted: #6a6258;
          }}

          * {{
            box-sizing: border-box;
          }}

          body {{
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 32px;
            font-family: "Space Grotesk", "Segoe UI", sans-serif;
            color: var(--ink);
            background:
              radial-gradient(800px 400px at 20% 20%, rgba(255, 255, 255, 0.7), transparent 60%),
              radial-gradient(800px 400px at 90% 10%, rgba(217, 108, 59, 0.15), transparent 50%),
              linear-gradient(160deg, var(--bg-top), var(--bg-bottom));
          }}

          .card {{
            width: min(900px, 95vw);
            background: var(--card);
            border-radius: 18px;
            padding: 36px;
            box-shadow:
              0 30px 60px rgba(31, 31, 31, 0.12),
              0 8px 16px rgba(31, 31, 31, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.06);
          }}

          h1 {{
            font-size: clamp(2rem, 3vw, 2.5rem);
            margin: 0 0 16px;
          }}

          pre {{
            background: #fbfaf8;
            border-radius: 12px;
            padding: 16px;
            overflow-x: auto;
            border: 1px solid rgba(0, 0, 0, 0.12);
            font-family: "JetBrains Mono", "Cascadia Mono", "Courier New", monospace;
            font-size: 0.95rem;
          }}

          a {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
          }}

          a:hover {{
            color: var(--accent-dark);
          }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Output</h1>
          <pre>{escaped}</pre>
          <a href="/">Back</a>
        </div>
      </body>
    </html>
    """
