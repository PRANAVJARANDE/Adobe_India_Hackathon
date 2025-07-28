FROM --platform=linux/amd64 python:3.9-slim

    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        HF_HOME=/app/.cache/huggingface \
        TRANSFORMERS_OFFLINE=1 \
        SENTENCE_TRANSFORMERS_HOME=/app/models

    WORKDIR /app

    COPY requirements.txt ./requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt

    # Pre-download and freeze the sentence-transformers model for offline use (Round 1B)
    RUN python - <<'PY'
from sentence_transformers import SentenceTransformer
m = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
m.save('/app/models/all-MiniLM-L6-v2')
print('Model saved to /app/models/all-MiniLM-L6-v2')
PY

    COPY . .

    ENTRYPOINT ["python", "main.py"]