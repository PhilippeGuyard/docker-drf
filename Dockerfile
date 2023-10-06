# Use an official Python runtime as a parent image
FROM python:3.9-alpine3.13

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PATH="/py/bin:$PATH"

# Install any needed packages specified in requirements.txt
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Define an argument for development mode
ARG DEV=false

# Install system dependencies and python packages
# Install libpq for runtime and other build dependencies
RUN apk add --update --no-cache libpq && \
    apk add --update --no-cache --virtual .tmp gcc build-base postgresql-dev musl-dev && \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ] ; then /py/bin/pip install -r /tmp/requirements.dev.txt ; fi && \
    apk del .tmp && \
    rm -rf /tmp



# Create Django user
RUN adduser --disabled-password --no-create-home django-user

# Switch to Django user
USER django-user

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app /app

# Make port 8000 available to the world outside this container
EXPOSE 8000
