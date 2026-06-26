FROM python:3.12-slim

WORKDIR /app

# Install certificate
COPY russian_trusted_root_ca_pem.crt /usr/local/share/ca-certificates/russian_root.crt
RUN update-ca-certificates

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "src.main"]
