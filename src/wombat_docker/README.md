# Mastodon Python App

Verify mastodon collection 

## Files
- mastodon_app.py: Main application
- Dockerfile: Container build instructions

## Build and Run

1. Build the Docker image:

   docker build -t mastodon .

2. Run the container:

   docker run --rm mastodon

The app will log a message every 15 seconds.
