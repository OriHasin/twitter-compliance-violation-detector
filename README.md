# Twitter Compliance Violation Detector

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)

A high-performance, AI-powered service that proactively detects social media policy violations to protect your organization's digital footprint and reputation.

## 🔍 Overview

The Twitter Compliance Violation Detector is a cybersecurity solution designed to help organizations monitor, detect, and manage potential policy violations in employee social media activity.  
By continuously scanning Twitter accounts against customizable compliance policies, this service uses advanced LLM to provide early warning of potential risks that could impact your organization's reputation, security posture, or regulatory compliance.

Upload your compliance policies and target Twitter account names, and our AI-powered engine will automatically detect and alert you to any policy violations.


## ✨ Core Features
- **Customizable Policies**: Define and upload your own compliance policies in JSON format with multiple rule categories.
- **AI-Powered Compliance Scanning**: Leverages OpenAI's advanced LLM to analyze tweets for policy violations with high accuracy.
- **Flexible Data Source:** Process tweets from real Twitter usernames concurrently or use pre-loaded sample data for demonstrations.
- **Violation Detection & Storage**: Automatically identifies, categorizes, and stores policy violations for immediate review.
- **RESTful API**: Well-documented API for easy integration with existing security workflows and dashboards.
- **Modular Unit Testing**: Clean unit-testing engine for the backend modules, can be extended easily.


## 💻 Tech Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: OpenAI API (default to 4o-mini model)
- **External APIs**: Twitter API v2
- **Infrastructure**: Docker, Docker Compose
- **Language**: Python 3.13
- **Testing**: Pytest with AsyncIO


## 🏗️ Architecture Best Practices

- **Clean Architecture**: Modular separation of concerns with different layers for maintainability. 
- **High Performance Async Processing**: Comprehensive asynchronous processing for large-scale I/O bound. 
- **Background Tasks**: Offloading long-running operations to background workers, user don't need to wait.
- **Isolated Database Access**: Secure concurrency connections handling with parameterized queries.
- **Environment Configuration**: Configuration via environment variables for security and flexibility.
- **Containerization**: Docker-based deployment for consistency across environments.



## 🚀 Deployment Guide

### Quick Start with Docker Compose

1. **Clone the repository**
   ```bash
   git clone https://github.com/OriHasin/twitter-compliance-violation-detector.git
   cd twitter-compliance-violation-detector
   ```

2. **Configure environment variables**
   Create a `.env` file in the project root with the following variables:
   ```
   # API Keys
   OPENAI_API_KEY=your_openai_api_key
   TWITTER_BEARER_TOKEN=your_twitter_bearer_token
   
   # Database Configuration
   DB_USER=user
   DB_PASSWORD=your_secure_password
   DB_HOST=db
   DB_PORT=5432
   DB_NAME=violation_db
   
   # Application Settings
   UPLOAD_DIR=data/compliance_policies/
   ```

3. **Launch with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the API**
   The API will be available at:
   ```
   http://localhost:8000/docs
   ```

## 📊 Core Workflow

NOTE: If you want to use Sample Tweets Data instead of real tweets fetching, just change USE_SAMPLE_DATA=True inside config.py

1. **Upload a compliance policy**
   ```bash
   # Example policy structure
   {
     "policy_name": "Social Media Policy",
     "rules": [
       {
         "rule_id": "CONF-001",
         "category": "Confidentiality",
         "description": "Sharing confidential information"
       },
       {
         "rule_id": "REP-001",
         "category": "Reputation",
         "description": "Damaging company reputation"
       }
     ]
   }
   ```

2. **Scan Twitter accounts**
   ```bash
   # Example request
   curl -X POST "http://localhost:8000/tweets/process" \
     -H "Content-Type: application/json" \
     -d '{"usernames": ["employee_handle"], "policy_name": "Social_Media_Policy"}'
   ```

3. **Review detected violations**
   ```bash
   curl -X GET "http://localhost:8000/tweets/violations"
   ```
   
4. More API endpoints are supported, please visit the docs.
