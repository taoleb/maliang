# Full image (browser, Node, etc.):
#   docker build -f docker/Dockerfile.latest -t maliang:latest .
#
# Lightweight image for the Web console only:
FROM python:3.11-slim-bookworm

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
EXPOSE 9899
CMD ["python", "app.py"]
