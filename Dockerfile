FROM python:alpine
COPY src /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["/app/entrypoint.sh"]
