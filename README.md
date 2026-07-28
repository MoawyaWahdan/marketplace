# Marketplace

## Live Demo

**Application:** https://marketplace-docker-c5ha.onrender.com/

**API Documentation (Swagger):**
https://marketplace-docker-c5ha.onrender.com/docs

---

# Project Overview

Marketplace is a backend-focused web application built with **FastAPI**.

The project demonstrates modern backend development practices, including RESTful API development, JWT authentication, PostgreSQL database management with Alembic migrations, Dockerized local development and deployment, CRUD operations, and Amazon S3 integration for image storage.

Users can:

* Register and authenticate
* Create marketplace listings
* Upload listing images
* Edit and delete their listings
* Browse available products

---

# Technologies

## Backend

* FastAPI
* Python
* PostgreSQL
* SQLAlchemy ORM
* Alembic
* JWT Authentication

## DevOps & Deployment

* Docker
* Docker Compose
* Render
* Neon PostgreSQL

## Cloud Storage

* Amazon S3

## Frontend

* HTML
* CSS
* JavaScript

---

# Features

* User registration
* JWT-based authentication
* Secure password hashing
* Create, update, and delete marketplace listings
* Upload and manage listing images
* Browse marketplace listings
* RESTful API
* Database migrations using Alembic
* Dockerized local development
* Docker deployment on Render

---

# Getting Started

## 1. Clone the repository

```bash
git clone <repository-url>
cd marketplace
```

## 2. Create the environment file

```bash
cp .env.example .env
```

Update the required values in `.env`.

## 3. Start the application

```bash
docker compose up --build
```

The application will automatically:

* Start PostgreSQL
* Apply Alembic migrations
* Start the FastAPI server

---

## 4. Open the application

Application:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## Stop the application

```bash
docker compose down
```

---

# Running Tests

Run the test suite inside the application container:

```bash
docker compose exec app pytest
```

---

# Deployment

The application is deployed on **Render** using **Docker** and connects to a managed **Neon PostgreSQL** database.

---

# Notes

* Create an account before creating listings.
* Docker Compose creates the local PostgreSQL environment automatically.
* Alembic migrations are applied automatically when the application starts.
* Listing images are stored in Amazon S3.
