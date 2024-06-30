FROM python:3.10.12

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /usr/src/app

COPY src ./src
COPY templates ./templates
COPY app.py .
COPY entrypoint.sh .

CMD ["python", "-m", "app"]

ENTRYPOINT [ "./entrypoint.sh" ]
