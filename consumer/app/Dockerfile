# ./app/Dockerfile
FROM python:3.9

WORKDIR /app

COPY . .

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 4040

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4040", "--workers", "1"]
