# JobShield — Job Advert Risk Checker

JobShield is a small, mobile-friendly Flask app that checks a pasted job advert, email, or message for common warning signs. It shows a 0–100 risk indicator, the matched wording, an explanation of each signal, and practical safety advice.

## Run in Replit

Start the **JobShield** web workflow. It launches the Flask app and uses the port supplied by the workspace.

## Requirements

- Python 3.13 or newer.
- Flask 3.1.3 or newer, below version 4, for the web app.
- Gunicorn 26.2 or newer, below version 27, for production serving. It is included in `requirements.txt`; local development can also use Flask's built-in server.
- The automated tests use Python's built-in `unittest` module; no separate test framework is required.

## Install and run locally

From the repository root, create a virtual environment and install the app requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r artifacts/jobshield/requirements.txt
python artifacts/jobshield/app.py
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1` instead of the `source` command. Then open the local address shown by Flask (port 5000 by default). Set `PORT` if your environment provides a different port.

## Run the tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests live in the repository-level `tests/` directory. The rule engine and Flask routes have automated tests, including input validation, bounded scoring, warning-sign evidence, security headers, and HTML escaping.

## Features

- Rule-based checks for upfront fees, guaranteed or unusually high earnings, urgent pressure, password/PIN/OTP requests, and unusual contact channels.
- A risk score from 0 to 100 and a plain-language risk category.
- Exact matched text and an explanation for each detected signal.
- Safe job-seeking reminders on the checker and results page.
- Mobile-first layout with a sample advert and character counter.
- Server-side validation, a 12,000-character limit, escaped HTML output, security headers, and no result-page caching.
- No database, account system, third-party AI service, advertising tracker, or external API.

## Privacy

Submitted advert text is handled in memory for the current request only. The app does not write adverts to a database or file, create a user account, or intentionally log submitted text. The results page is marked `no-store`. Users should still remove names, phone numbers, addresses, and other personal details before pasting content.

## How the score works

Each distinct warning-sign category adds a fixed number of points: upfront payment (35), credential request (35), guaranteed/high earnings (20), urgency (15), and unusual contact method (15). The total is capped at 100. Some nearby wording that explicitly rejects a warning (for example, “never share your password”) is ignored.

Categories are Low (0–19), Elevated (20–44), High (45–69), and Very high (70–100). These values are a simple rule-based signal, not a probability or a judgment about a specific employer.

## Limitations

- This is an automated preliminary check, not proof of fraud.
- JobShield cannot verify whether a company, recruiter, website, or vacancy is legitimate.
- A low score does not guarantee an offer is safe, and a higher score does not prove fraud.
- The rules look for selected phrases and can miss reworded, translated, image-based, or new scam patterns. They can also flag legitimate wording without enough context.
- The score is not a statistical probability, financial advice, or legal advice. Verify an offer through contact details you find independently.
