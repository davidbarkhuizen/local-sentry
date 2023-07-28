#!/bin/bash

echo "updating dependencies via poetry" 
poetry update

echo "launching local sentry"
LOCAL_SENTRY_LOG_FILE_FOLDER_PATH="${HOME}/Library/Logs/local-sentry" poetry run python local_sentry/local_sentry.py