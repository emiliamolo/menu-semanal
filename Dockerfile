FROM python:3.10-slim

WORKDIR /app

# Instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto de Flask
EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]