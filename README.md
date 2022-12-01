# Sound check app (find similar audio files)

## Description

This application was originally created as a CLI application to search for duplicate audio files in the local music library. <br/>
Now it was rewritten as DRF (Django REST framework) based app.

## Requirements

- Python 3.10
- PostgreSQL
- Docker (with docker-compose)

## Setup

0. Create env and install requirements
1. Set up your variables in .env file or use default.
2. Create database with your name (default: sound_fingerprints)
3. Run docker-compose
4. Make migrations and migrate
5. Run Celery
6. Run main app


## Usage

Go to the browser /api/v1/songs/ or /api/v1/swagger/ for swagger.