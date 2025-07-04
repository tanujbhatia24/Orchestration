# MERN Stack Deployment on AWS with Docker, Jenkins, EKS & DevOps Automation
This project demonstrates how to deploy a full-stack MERN (MongoDB, Express, React, Node.js) application using AWS infrastructure, Docker containers, CI/CD with Jenkins, Kubernetes (EKS), and automation using Python Boto3 scripts. It includes infrastructure-as-code, monitoring, backup automation, and ChatOps.

---
## Project Overview
This project shows how to build and deploy a production-grade MERN stack app with:
- Containerization using Docker
- Version control using AWS CodeCommit
- CI/CD using Jenkins and Amazon ECR
- Infrastructure provisioning with Boto3 (Python)
- EKS (Kubernetes) deployment with Helm
- Monitoring, backups, and notifications using CloudWatch, Lambda, S3, and SNS

---
## Tech Stack
- **Frontend:** React (Dockerized)
- **Backend:** Node.js + Express (Dockerized)
- **Database:** MongoDB
- **Infrastructure:** AWS (EC2, VPC, ECR, S3, Route 53, ALB, Lambda, EKS)
- **CI/CD:** Jenkins, CodeCommit
- **IaC:** Python + Boto3
- **Monitoring:** CloudWatch
- **Notifications:** SNS, SES, Slack (ChatOps)

---
## Infrastructure Components
| Component            | Service                |
|---------------------|------------------------|
| Source Control       | GitHub         |
| CI/CD                | Jenkins on EC2         |
| Containers           | Docker, Amazon ECR     |
| Compute              | EC2, Auto Scaling Group|
| Load Balancer        | Application Load Balancer (ALB) |
| Networking           | VPC, Subnets, Security Groups |
| DNS                  | Cloudflare               |
| Kubernetes (optional)| Amazon EKS, Minikube             |
| Monitoring           | CloudWatch             |
| Notifications        | SNS + Lambda + Slack   |
| Backup               | MongoDB dump via Lambda to S3 |

---
## Setup Guide
### Step 1: AWS CLI & Boto3 Setup
```bash
aws configure
pip install boto3
```
### Step 2: Dockerize the MERN App
- App Source code repo URL - "https://github.com/tanujbhatia24/SampleMERNwithMicroservices.git"
- Dockerfile for frontend
- Dockerfile for backend

### Step 3: Push Docker Images to ECR
```bash
# Create repos
aws ecr create-repository --repository-name <repo-name>

# Authenticate & push
aws ecr get-login-password | docker login --username AWS <ecr-url>
docker build -t <name> .
docker tag <name> <ecr-url>
docker push <ecr-url>
```

### Step 4:  Set Up CodeCommit/Github repo
- NOTE: Used GIT instead of CodeComiit.

### Step 5: Jenkins CI/CD
- Jenkins installed on EC2 OR use HeroVired Jenkins
- Jobs:
  - Build & push Docker images
  - Trigger on CodeCommit webhook

### Step 6: Infrastructure Provisioning with Boto3
- Python scripts to create:
  - VPC, subnets
  - Security groups
  - EC2 Launch Templates
  - Auto Scaling Group for backend
  - ELB

### Step 7: Deploy Frontend and Backend
- Backend on EC2 (Auto Scaling Group)
- Frontend on EC2
- Use user_data in EC2 to run Docker container

### Step 8: Set Up Load Balancer and DNS
- ALB routes traffic to backend
- Route 53/Cloudflare maps domain to ALB

### Step 9: MongoDB Backup with Lambda
- Lambda dumps MongoDB → uploads to S3
- Triggered daily via CloudWatch Events

---
## CI/CD Pipeline
**Use Jenkinsfile for CI/CD**
```mermaid
graph TD
A[Developer Commit] --> B[Github Repo]
B --> C[Jenkins Triggered]
C --> D[Build Docker Images]
D --> E[Push to Amazon ECR]
E --> F[Deploy to EC2/EKS]
F --> G[Success OR Failure Notify]
```
---
## Infrastructure as Code (IaC)
All infrastructure is defined using Python + Boto3 scripts:
- create_infra.py
- lambda-mongo-backup/function.zip
- destroy_infra.py
  
Run with: python create_infra.py<br>
Run with: python destroy_infra.py<br>
Use lambda-mongo-backup/function.zip to create lambda DB backup function.<br>

---
## Monitoring & Logging
- CloudWatch Logs: Collect logs from EC2.
- CloudWatch Alarms: Trigger alerts on high CPU etc.
- CloudWatch Dashboards: Optional for visualization.

---
## ChatOps Integration
- SNS topics for deployment events
- Lambda notifies Slack/MS Teams/Telegram via webhook [You can use lambda_SNS.py]
- SES configured for email alerts (e.g., failed backups)

---
## Security Best Practices
- Use IAM Roles instead of hardcoded credentials
- Open only required ports in security groups (e.g., 80, 22)
- Use HTTPS with SSL (ACM + ALB)
- Keep secrets in AWS Secrets Manager or SSM Parameter Store

---
## Final Validation Checklist
- Frontend accessible via domain
- Backend responds correctly
- Docker images present in ECR
- CI/CD triggers on commits
- Logs visible in CloudWatch
- Backup stored in S3
- Notifications received

---
## Snapshot for validation
- **Infrastructure as Code (IaC) with Boto3**<br>
<img width="325" alt="image" src="https://github.com/user-attachments/assets/929a836f-2a9f-4b86-b0d6-703e1790831a" /><br>
<img width="704" alt="image" src="https://github.com/user-attachments/assets/52899d7a-d45c-4d90-abb4-3de080b5eaf8" /><br>
<img width="662" alt="image" src="https://github.com/user-attachments/assets/f10e9b5d-db5f-41e0-a286-be908c7f56bf" /><br>
<img width="755" alt="image" src="https://github.com/user-attachments/assets/f88ca665-18bc-4ce1-a919-ddb8b1d89d48" /><br>
<img width="845" alt="image" src="https://github.com/user-attachments/assets/a281e83f-facd-4b40-adf0-627bee07f8f7" /><br>

- **Backend & Frontend on EC2s**<br>
<img width="658" alt="image" src="https://github.com/user-attachments/assets/453c666c-4b02-40b8-ba61-210e3fc4366a" /><br>
<img width="656" alt="image" src="https://github.com/user-attachments/assets/c40970d2-de55-421c-b2fb-cf17acbcb27e" /><br>

- **EC2 IAM role**<br>
<img width="815" alt="image" src="https://github.com/user-attachments/assets/1829e504-6acc-4199-95f1-f34cf9cc7038" /><br>

- **Terminated one Backend and ASG created a new one immediately**<br>
<img width="672" alt="image" src="https://github.com/user-attachments/assets/47ce3e55-8841-47dd-a88e-fdb1bfd8de3c" /><br>

- **ECS IMAGE**<br>
![image](https://github.com/user-attachments/assets/46e0b996-dca0-4318-ac1d-5d2594ee41e9)<br>
![image](https://github.com/user-attachments/assets/53a0fc20-50e0-4b13-92ee-086a42aaadb2)<br>

- **Docker container running status**<br>
![image](https://github.com/user-attachments/assets/57bae206-f3e6-4a96-9f7e-01fcad78defe)<br>
<img width="174" alt="image" src="https://github.com/user-attachments/assets/d9465dd2-0c91-461f-b683-1635828ee3de" /><br>
![image](https://github.com/user-attachments/assets/374c32a0-2990-4f72-9ab9-16947b2ca362)<br>
<img width="182" alt="image" src="https://github.com/user-attachments/assets/af0ad436-7faa-491d-b7c0-05d6a21de6d0" /><br>
![image](https://github.com/user-attachments/assets/e9f78d23-4bc3-4766-813e-d53a12a17b1c)<br>
<img width="632" alt="image" src="https://github.com/user-attachments/assets/e7c77a7b-3af5-4fba-8536-44f59ad0c94b" /><br>

- **Load Balance & Target Group for backend service**<br>
<img width="841" alt="image" src="https://github.com/user-attachments/assets/9413eb3d-9733-4e7b-9778-1c32d2bd977c" /><br>
![image](https://github.com/user-attachments/assets/ae5e360f-09a3-4378-86ac-130c1d528484)<br>
<img width="329" alt="image" src="https://github.com/user-attachments/assets/a1e87d25-0eff-4b1f-a363-581df660bf00" /><br>

- **DNS setup**<br>
![image](https://github.com/user-attachments/assets/095dad42-f0fb-462f-a099-9b8a7cfc0e69)<br>
![image](https://github.com/user-attachments/assets/29ea9a52-0048-4984-8b3c-ab7ba21dfe42)<br>

- **Backup of Db using Lambda Functions**<br>
![image](https://github.com/user-attachments/assets/f84c41dc-bf4f-4d9d-9dd5-a4ab7387a9b1)<br>
![image](https://github.com/user-attachments/assets/d724a184-064d-435c-ba2a-0f55d5cf02bf)<br>

- **EKS** <br>
<img width="677" alt="image" src="https://github.com/user-attachments/assets/2b5d1f32-870d-40cd-8330-759681f0f47e" /><br>
<img width="473" alt="image" src="https://github.com/user-attachments/assets/4f260c0f-f939-4f95-b039-a2c2cf47f148" /><br>
  - backend<br>
<img width="438" alt="image" src="https://github.com/user-attachments/assets/3ab60033-a0a6-4898-bd98-b616058058b8" /><br>
<img width="272" alt="image" src="https://github.com/user-attachments/assets/90227bb4-2c39-43a5-b0ef-5791600b2fa2" /><br>
  - frontend<br>
<img width="650" alt="image" src="https://github.com/user-attachments/assets/97b36a5f-0468-4693-b7ab-3b1bdf1e4faa" /><br>
<img width="443" alt="image" src="https://github.com/user-attachments/assets/98530185-f02d-4463-ac36-b2ab3ee1773c" /><br>

- **Cloudwatch Monitoring, Alerting & Logging**<br> 
<img width="680" alt="image" src="https://github.com/user-attachments/assets/33f17c2c-e358-46c0-97ff-47862ac204e7" /><br>
<img width="896" alt="image" src="https://github.com/user-attachments/assets/f8e68132-ae55-4fef-bf76-d23f2b1a8ad8" /><br>
![image](https://github.com/user-attachments/assets/0f5426c0-7bf6-42d5-a3c6-e1ed2712daed)<br>

- **ChatOps Integration (Telegram)**<br>
<img width="752" alt="image" src="https://github.com/user-attachments/assets/40205d9a-783a-438e-81cc-cbaf94e8d7da" /><br>
![image](https://github.com/user-attachments/assets/09bd5834-1183-450d-9de5-69c956f5293a)<br>
<img width="956" alt="image" src="https://github.com/user-attachments/assets/2cd68738-fc79-4f9e-905f-f787e7a3fd46" /><br>

- **Destroying INFRA**<br>
<img width="323" alt="image" src="https://github.com/user-attachments/assets/4cf0b68e-cc84-453e-b747-42f14b581833" /><br>
<img width="742" alt="image" src="https://github.com/user-attachments/assets/f9bca2eb-0eb8-4e1c-b105-890eb5d75980" /><br>

---
## Author
Tanuj Bhatia
