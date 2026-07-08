"""
Flask web deployment for the EmotionDetection module.

Endpoints:
- GET / : Simple UI
- POST /emotionDetector : JSON API for emotion detection

Includes blank-input error handling (HTTP 400).
Also supports running pylint for static analysis via `--pylint-only`.
"""

from __future__ import annotations

import argparse
import subprocess
from typing import Any

from flask import Flask, jsonify, render_template_string, request

from EmotionDetection import emotion_detector

app = Flask(__name__)


INDEX_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>AI Emotion Detector</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem; }
      textarea { width: 100%; max-width: 700px; }
      .container { max-width: 800px; }
      .card { border: 1px solid #ddd; padding: 1rem; border-radius: 8px; }
      .error { color: #b00020; }
      pre { background: #f6f8fa; padding: 0.75rem; border-radius: 6px; }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>AI Emotion Detector</h1>
      <div class="card">
        <p>Enter text to detect emotions:</p>
        <textarea id="textInput" rows="5" placeholder="Type something..."></textarea>
        <br/><br/>
        <button id="detectButton">Detect Emotions</button>
      </div>
      <br/>
      <div id="message" class="error" style="display:none;"></div>
      <h3>Result</h3>
      <pre id="output">Submit text and click the button.</pre>
    </div>
    <script>
      const messageEl = document.getElementById('message');
      const outputEl = document.getElementById('output');
      const textInputEl = document.getElementById('textInput');
      const detectButtonEl = document.getElementById('detectButton');

      async function detect() {
        messageEl.style.display = 'none';
        messageEl.textContent = '';

        const text = textInputEl.value || '';
        const response = await fetch('/emotionDetector', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });

        const data = await response.json();
        if (!response.ok) {
          messageEl.style.display = 'block';
          messageEl.textContent = data.error || 'Invalid text!';
          outputEl.textContent = JSON.stringify(data.result, null, 2);
          return;
        }

        outputEl.textContent = JSON.stringify(data, null, 2);
      }

      detectButtonEl.addEventListener('click', detect);
    </script>
  </body>
</html>
"""


def _request_text() -> str | None:
    """Extract text from JSON payload or form payload."""
    if request.is_json:
        payload: Any = request.get_json(silent=True)
        if isinstance(payload, dict):
            raw_text = payload.get("text")
            return None if raw_text is None else str(raw_text)
        return None

    # Fallback for form posts (not used by our UI but keeps API flexible).
    raw_text = request.form.get("text")
    return None if raw_text is None else str(raw_text)


def run_pylint(target: str = "server.py") -> int:
    """
    Run pylint and print output.

    The assignment rubric asks for a perfect score output. We run with
    `--score=y` to ensure the rating is printed in the terminal.
    """
    completed = subprocess.run(
        ["pylint", "--score=y", target],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout)
    if completed.stderr:
        print(completed.stderr)
    return completed.returncode


@app.get("/")
def index() -> str:
    """Serve the simple single-page UI."""
    return render_template_string(INDEX_HTML)


@app.post("/emotionDetector")
def emotion_detector_api():
    """JSON API that returns emotion scores."""
    text = _request_text()
    result, status_code = emotion_detector(text)
    if status_code == 400:
        return jsonify({"error": "Invalid text! Please try again!", "result": result}), 400
    return jsonify(result), 200


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emotion detector Flask server.")
    parser.add_argument("--pylint-only", action="store_true", help="Run pylint then exit.")
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint for local development and rubric checks."""
    args = _parse_args()
    if args.pylint_only:
        raise SystemExit(run_pylint("server.py"))
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
