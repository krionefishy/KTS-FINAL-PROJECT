FROM python:3.12-slim


WORKDIR /code


RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    net-tools \ 
    procps \ 
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/code


CMD ["python", "/code/main.py"]   