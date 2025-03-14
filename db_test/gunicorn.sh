#!/bin/bash

# Run Gunicorn with 4 workers
exec gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
