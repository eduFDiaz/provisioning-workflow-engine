FROM python:3.8-slim-buster

WORKDIR /producer

COPY . /producer

RUN pip install -r ./requirements.txt

CMD ["python", "./Producer.py"]