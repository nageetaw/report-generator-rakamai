FROM python:3.11-slim

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

RUN useradd -m myuser && chown -R myuser /app
USER myuser

EXPOSE 8000

CMD ["./start.sh"]
