FROM python:3.13-alpine

WORKDIR /app

RUN apk add --no-cache \
    nodejs \
    npm \
    bash

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Serverless config before installing plugins
COPY serverless.yml /app/serverless.yml

# Install Serverless Framework globally
RUN npm install -g serverless

# Install Serverless plugins
RUN serverless plugin install -n serverless-wsgi && \
    serverless plugin install -n serverless-ssm-fetch && \
    serverless plugin install -n serverless-python-requirements

COPY . /app

EXPOSE 5000

CMD ["flask", "--app", "api/app.py", "run", "-h", "0.0.0.0", "-p", "5000"]