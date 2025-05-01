FROM python:latest
WORKDIR /CloudflareDNSupdater

COPY CloudflareDNSupdater.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "-u", "./CloudflareDNSupdater.py"]