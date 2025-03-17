# Flask API Deployment to AWS Lambda with Serverless Framework

This project demonstrates how a simple Flask API can be deployed to **AWS Lambda** using the **Serverless Framework**.

## 🚀 Setup

### 1. Create and Load Environment Variables

Lambda function needs to have API_KEY variable set up. To do this, we utilize AWS Systems Manager Parameter Store. The variable can be set with:
```sh
aws ssm put-parameter --name "/flask-serverless-lambda/api-key" --value "your-api-key-value" --type SecureString
```
The value does not matter.
- Copy the example environment file:
  ```sh
  cp env.example .env
  ```
- Edit `.env` and add your environment variables.
- Load the variables into your shell:
  ```sh
  source .env
  ```

### 2. Build and Run the Docker Container
- Build the Docker image:
  ```sh
  docker compose build
  ```
- Start the container:
  ```sh
  docker compose up -d
  ```
- The API will be available at:
  ```
  http://127.0.0.1:${PORT}/home
  ```

### 3. Access the Running Container
To enter the container shell:
```sh
docker compose exec app bash
```

### 4. Deploy to AWS Lambda
To deploy the API using **Serverless Framework**, run:
```sh
serverless deploy
```

## 🔑 GitHub Actions & Manual Deployment
For **GitHub Actions** and manual deployments to work correctly, ensure that all necessary environment variables are set as **GitHub Action Secrets**.

---

## 🛠 Technologies Used
- **Flask** – Web framework for Python
- **Docker** – Containerization for local development
- **Serverless Framework** – Deployment automation for AWS Lambda
- **AWS Lambda** – Serverless compute service

## 📄 License
This project is licensed under the MIT License.

---

### 📌 Notes
- If you need to **update environment variables**, update `.env` and restart the container with:
  ```sh
  docker compose up -d --build
  ```
- For debugging deployment issues, check logs with:
  ```sh
  serverless logs -f function_name
  ```
