FROM python:3.12-slim

RUN pip install --no-cache-dir pyftpdlib==2.2.0

WORKDIR /app
COPY server.py .

EXPOSE 21 30000-30009
CMD ["python", "-u", "server.py"]
