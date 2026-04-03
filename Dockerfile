FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV INPUT_CSV=data/candidates.csv
ENV OUTPUT_CSV=output/ranked_candidates.csv

CMD ["python", "app/main.py"]
