FROM python:3.13-alpine

WORKDIR /app

COPY requirements /app/requirements
RUN pip install --no-cache-dir -r requirements/requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python", "-m", "api.app"]