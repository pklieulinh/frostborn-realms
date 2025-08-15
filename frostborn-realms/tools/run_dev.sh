#!/usr/bin/env bash
export PYTHONUNBUFFERED=1
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000