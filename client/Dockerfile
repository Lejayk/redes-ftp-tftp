FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8080
# --loop asyncio: uvloop no implementa sock_sendto ni sock_recvfrom, que usa el cliente tftp
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--loop", "asyncio", "--no-access-log"]
