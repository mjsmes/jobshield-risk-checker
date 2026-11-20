FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY artifacts/jobshield/requirements.lock ./requirements.lock

RUN pip install --no-cache-dir --require-hashes -r requirements.lock \
    && useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser artifacts/jobshield/app.py ./app.py
COPY --chown=appuser:appuser artifacts/jobshield/analysis_engine.py ./analysis_engine.py
COPY --chown=appuser:appuser artifacts/jobshield/templates ./templates
COPY --chown=appuser:appuser artifacts/jobshield/static ./static

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --access-logfile - --error-logfile - app:app"]
