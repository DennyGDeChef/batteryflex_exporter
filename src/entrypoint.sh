#!/bin/sh
gunicorn --chdir /app -w 2 --threads 2 -b 0.0.0.0:9988 batteryflex:app
