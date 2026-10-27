# JobShield — Job Advert Risk Checker

A privacy-first Flask app that checks pasted job adverts and messages for common warning signs before a job seeker shares personal information or pays a fee.

## Run & Operate

- Start the **JobShield** web workflow to run the app in the preview.
- `cd artifacts/jobshield && python3 -m unittest discover -s tests -v` — run the automated tests.

## Stack

- Python 3.13 and Flask
- Jinja HTML templates and responsive CSS
- Rule-based analysis only; no external AI or paid API
- No database, login, or advert storage

## Where things live

- `artifacts/jobshield/analysis_engine.py` — warning-sign rules and risk scoring.
- `artifacts/jobshield/app.py` — Flask routes, request validation, and response headers.
- `artifacts/jobshield/templates/` — checker and results pages.
- `artifacts/jobshield/static/` — local styles, sample-text behavior, and favicon.
- `artifacts/jobshield/tests/` — automated engine and route tests.
- `artifacts/jobshield/README.md` — setup, feature, privacy, and limitation details.

## Product

JobShield analyzes a pasted job advert, email, or chat message for upfront payment requests, guaranteed or unusually high earnings, pressure to act immediately, requests for account credentials, and unusual contact methods. It displays a 0–100 risk indicator, matched wording, plain-language explanations, and safer next steps.

This is an automated preliminary check. It is not proof of fraud and does not verify a company's legitimacy.

## Architecture decisions

- Submitted text is analyzed in memory and is not written to a database or file.
- A fixed, explainable rule set is used instead of external services.
- Jinja autoescaping is kept enabled, and result responses are marked `no-store`.
- Risk points represent matched warning-sign categories, not a probability.
