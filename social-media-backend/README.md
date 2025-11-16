# Social Media Feed Backend (Project Nexus)

A backend service built for managing posts, comments, likes, and user interactions using **Django** and **GraphQL**.  
This project is part of the **ProDev Backend Engineering Program – Project Nexus**, focusing on scalable backend design and flexible GraphQL APIs.

---

## Project Overview

This project implements the backend for a social media feed system.  
It supports:

- Creating and managing posts  
- Interactions such as likes and comments  
- Flexible and optimized data querying using GraphQL  
- Scalable database structure suitable for high-traffic apps  
- Asynchronous background tasks using Celery and Redis  

The backend is designed following industry best practices in API architecture, security, environment configuration, and version control.

---

## Project Goals

- **Post Management:** Create, fetch, and manage social media posts  
- **Flexible Querying:** Use GraphQL for advanced and predictable data queries  
- **Scalability:** Optimize the database schema for future growth and high user activity  
- **Asynchronous Processing:** Handle notifications, feed updates, and analytics efficiently  

---

## Technologies Used

| Technology | Purpose |
|-----------|---------|
| **Python 3.9+** | Core programming language for backend development |
| **Django 5.x** | Main backend web framework |
| **PostgreSQL 14+** | Relational database for storing posts, users, and interactions |
| **GraphQL (Graphene-Django)** | Flexible API query layer for posts, comments, and interactions |
| **GraphQL Playground** | Testing GraphQL queries and mutations |
| **Celery 6+** | Asynchronous task queue for background jobs (e.g., notifications, updating feeds) |
| **Redis 7+** | Message broker and caching backend for Celery tasks |
| **Python-Decouple / dotenv** | Environment variable management for secrets and configuration |
| **Docker** | Containerization for development and deployment |
| **Git & GitHub** | Version control and collaboration |

---

## Project Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Lawremwashail/social-media-backend.git
cd social-media-backend

### 2 Create and Activate Virtual Environment
python3 -m venv venv
source venv/bin/activate

### 3 Install Dependencies
pip install -r requirements.txt

### 4 Configure Environment Variables
- Create .env file in the root of the directory
- Include the following in the .env file:

SECRET_KEY=your_secret_key
DB_NAME=social_media_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

### 5 Apply Migrations
python manage.py migrate

### 6 Run Development Server
python manage.py runserver

### 7 Run Celery Worker
celery -A core worker --beat --scheduler django --loglevel=info

---

