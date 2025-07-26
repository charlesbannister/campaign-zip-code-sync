# Deployment Guide

## 1. Containerize with Docker

1. Create a `Dockerfile` in the project root:
   ```Dockerfile
   # Use official Python image
   FROM python:3.11-slim
   WORKDIR /app
   COPY . /app
   RUN pip install --upgrade pip && pip install poetry \
       && poetry install --no-dev
   CMD ["python", "-m", "zip_sync"]
   ```
2. Build the Docker image:
   ```sh
   docker build -t campaign-zip-code-sync .
   ```
3. Run the container locally:
   ```sh
   docker run --rm campaign-zip-code-sync
   ```

## 2. Deploy to DigitalOcean Droplet

1. Create a new Ubuntu droplet on DigitalOcean.
2. SSH into the droplet:
   ```sh
   ssh root@your_droplet_ip
   ```
3. Install Docker:
   ```sh
   curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
   ```
4. Pull your Docker image (after pushing to a registry, e.g., Docker Hub):
   ```sh
   docker pull yourdockerhubuser/campaign-zip-code-sync:latest
   ```
5. Run the container:
   ```sh
   docker run --rm yourdockerhubuser/campaign-zip-code-sync:latest
   ```

## 3. Set Up GitHub Actions CI/CD

1. In your repo, create `.github/workflows/deploy.yml`:
   ```yaml
   name: CI/CD Pipeline
   on:
     push:
       branches: [main]
   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: "3.11"
         - name: Install Poetry
           run: pip install poetry
         - name: Install dependencies
           run: poetry install --no-dev
         - name: Build Docker image
           run: docker build -t campaign-zip-code-sync .
         - name: Log in to Docker Hub
           run: echo ${{ secrets.DOCKERHUB_TOKEN }} | docker login -u ${{ secrets.DOCKERHUB_USERNAME }} --password-stdin
         - name: Push Docker image
           run: docker tag campaign-zip-code-sync yourdockerhubuser/campaign-zip-code-sync:latest && docker push yourdockerhubuser/campaign-zip-code-sync:latest
         # Optionally, add SSH deploy step to restart container on droplet
   ```
2. Add your Docker Hub credentials as GitHub secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`.
3. (Optional) Add SSH keys/secrets for remote deployment.

## 4. Schedule with Cron (every 15 minutes)

On your droplet, add this to your crontab (edit with `crontab -e`):

```
*/15 * * * * docker run --rm yourdockerhubuser/campaign-zip-code-sync:latest
```

This will run the container every 15 minutes.
