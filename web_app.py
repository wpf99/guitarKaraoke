#!/usr/bin/env python3
import os
import secrets
from pathlib import Path
from flask import Flask, render_template_string, request, send_from_directory

from remove_guitar import remove_guitar


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

PAGE_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Remove Guitar (Demucs)</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 40px; }
      .card { max-width: 720px; padding: 24px; border: 1px solid #ddd; border-radius: 8px; }
      .row { margin-top: 18px; }
      audio { width: 100%; }
      .error { color: #b00020; }
    </style>
  </head>
  <body>
    <div class="card">
      <h2>Remove Guitar (Approx)</h2>
      <p>This mixes drums + bass + vocals from Demucs to reduce guitar.</p>
      <form method="post" enctype="multipart/form-data">
        <input type="file" name="audio_file" accept="audio/*" required>
        <button type="submit">Process</button>
      </form>

      {% if error %}
        <div class="row error">{{ error }}</div>
      {% endif %}

      {% if original_url and output_url %}
        <div class="row">
          <strong>Original</strong>
          <audio controls src="{{ original_url }}"></audio>
        </div>
        <div class="row">
          <strong>No Guitar (Approx)</strong>
          <audio controls src="{{ output_url }}"></audio>
        </div>
      {% endif %}
    </div>
  </body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        audio_file = request.files.get("audio_file")
        if not audio_file:
            return render_template_string(PAGE_TEMPLATE, error="No file provided.")

        token = secrets.token_hex(4)
        safe_name = f"{token}_{Path(audio_file.filename).name}"
        upload_path = UPLOAD_DIR / safe_name
        audio_file.save(upload_path)

        output_name = f"{upload_path.stem}_no_guitar.mp3"
        output_path = OUTPUT_DIR / output_name

        try:
            remove_guitar(upload_path, output_path, model="htdemucs")
        except Exception as exc:
            return render_template_string(PAGE_TEMPLATE, error=str(exc))

        original_url = f"/uploads/{upload_path.name}"
        output_url = f"/outputs/{output_name}"
        return render_template_string(
            PAGE_TEMPLATE, original_url=original_url, output_url=output_url
        )

    return render_template_string(PAGE_TEMPLATE, original_url=None, output_url=None)


@app.route("/uploads/<path:filename>")
def get_upload(filename: str):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/outputs/<path:filename>")
def get_output(filename: str):
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
