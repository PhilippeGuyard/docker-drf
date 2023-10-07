# Docker-DRF Boilerplate Project

## Overview

This is a boilerplate project for quickly getting started with building RESTful APIs using Django Rest Framework (DRF). The project includes:

- Docker and Docker Compose setup for easier development and deployment
- GitHub Actions for CI/CD
- Custom User Model
- JWT Authentication
- Swagger and drf-spectacular for API documentation
- Uses a custom Admin URL (from env. vars)

## Prerequisites

- Docker and Docker Compose
- PostgreSQL (Containerized)

## Setup

### Clone the Repository

\```bash
git clone https://github.com/PhilippeGuyard/docker-drf.git
\```

### Using Docker Compose

This project is configured to run with Docker Compose, including a containerized PostgreSQL database.

Navigate to the project directory and run:

\```bash
docker-compose up --build
\```

Your Django application and PostgreSQL database should now be running in their own containers.

### Manual Setup

Manual setup is not recommended as the project is designed to work with Docker Compose.

## Features

### Custom User Model

A custom user model is provided for more flexibility.

### JWT Authentication

JWT-based authentication is configured and ready to use.

### API Documentation

API documentation is available through Swagger and drf-spectacular. Access it at `http://localhost:8000/api/docs`.

## GitHub Actions

This project includes GitHub Actions for continuous integration and deployment. Check `.github/workflows` for the workflow definitions.

## Directory Structure

The main project directory is `app`.

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcomed.

## License

MIT License

Copyright (c) 2023 Philippe Guyard

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

