FROM python:3.10.12

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /usr/src/app

COPY app.py .
COPY entrypoint.sh .

ENTRYPOINT [ "./entrypoint.sh" ]
CMD [ "opentelemetry-instrument", "python", "-m", "app" ]
