FROM python:3.10-slim

# https://stackoverflow.com/questions/46711990/error-pg-config-executable-not-found-when-installing-psycopg2-on-alpine-in-dock
RUN apt-get update && apt-get install -y \
    #had chatgpt help determine what was needed to support postgis
    libpq-dev gcc \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev && \
    rm -rf /var/lib/apt/lists/*


ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]