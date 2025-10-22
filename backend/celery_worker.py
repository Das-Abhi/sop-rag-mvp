#!/usr/bin/env python
"""
Celery worker starter script
Usage: python celery_worker.py
"""
import os
import sys
from app.celery_app import app

if __name__ == "__main__":
    # Set concurrency for development (single worker)
    concurrency = int(os.getenv("CELERY_CONCURRENCY", 2))

    app.worker_main([
        "worker",
        "--loglevel=info",
        f"--concurrency={concurrency}",
        "--prefetch-multiplier=1",
    ])
