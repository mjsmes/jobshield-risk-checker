"""Flask web application for JobShield."""

from __future__ import annotations

import os

from analysis_engine import MAX_TEXT_LENGTH, analyze_text
from flask import Flask, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 65_536
app.config["MAX_TEXT_LENGTH"] = MAX_TEXT_LENGTH


@app.after_request
def set_safety_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; base-uri 'none'; form-action 'self'; "
        "frame-ancestors 'none'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; object-src 'none'"
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    return response


@app.get("/")
def home():
    return render_template("index.html", max_text_length=MAX_TEXT_LENGTH)


@app.post("/check")
def check_advert():
    submitted_text = request.form.get("job_text", "")

    if not submitted_text.strip():
        return (
            render_template(
                "index.html",
                max_text_length=MAX_TEXT_LENGTH,
                error="Paste a job advert or message before checking it.",
            ),
            400,
        )

    if len(submitted_text) > MAX_TEXT_LENGTH:
        return (
            render_template(
                "index.html",
                max_text_length=MAX_TEXT_LENGTH,
                error=f"Please keep your text to {MAX_TEXT_LENGTH:,} characters or fewer.",
            ),
            400,
        )

    result = analyze_text(submitted_text)
    return render_template("results.html", result=result)


@app.errorhandler(RequestEntityTooLarge)
def request_too_large(_error):
    return (
        render_template(
            "index.html",
            max_text_length=MAX_TEXT_LENGTH,
            error=f"That message is too large. Please keep it to {MAX_TEXT_LENGTH:,} characters or fewer.",
        ),
        413,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
    )
