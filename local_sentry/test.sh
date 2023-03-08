/bin/bash

NB: run in activated venv

function kill_all_procs_listening_on_port()
{
    PORT_NUMBER=9000
    lsof -i tcp:${PORT_NUMBER} | awk 'NR!=1 {print $2}' | xargs kill 
}

python3 -m pip install -r requirements.txt
LOCAL_SENTRY_LOG_FILE_FOLDER_PATH="${HOME}/Library/Logs/local-sentry" python3 local_sentry.py & pytest
kill_all_procs_listening_on_port

LOCAL_SENTRY_LOG_FILE_FOLDER_PATH="${HOME}/Library/Logs/local-sentry" python3 pytest