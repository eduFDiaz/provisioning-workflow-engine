FROM python:3.10

WORKDIR /app

COPY requirements.txt .
#RUN pip install --upgrade pip
#RUN python3 -m pip install --upgrade setuptools

RUN apt-get update && \
  apt-get install -y --no-install-recommends gcc git libssl-dev g++ make && \
  cd /tmp && git clone https://github.com/edenhill/librdkafka.git && \
  cd librdkafka && git checkout tags/v2.3.0 && \
  ./configure && make && make install && \
  cd ../ && rm -rf librdkafka

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--env-file", "env/app-docker.properties"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--env-file", "config/dev.conf"]
