from fastapi import FastAPI, Request, HTTPException
import uvicorn
from datetime import datetime
import os
import uuid
from enum import Enum
import logging
import zlib
import json

api = FastAPI()

server = None

from enum import Enum

class Endpoint(Enum):
    ENVELOP = 'envelop'
    STORE = 'store'
    MINIDUMP = 'minidump'

local_logger = None
log_file_path = None

def configure_logging(log_file_folder_path: str):
    
    global local_logger
    global log_file_path

    print(f'local-sentry examining log folder @ {log_file_folder_path}')

    if not os.path.exists(log_file_folder_path):
        print(f'does not exist, creating')
        os.makedirs(log_file_folder_path)

    log_file_path = os.path.join(log_file_folder_path, 'local-sentry-client-logs.log')
    print(f'local-sentry: logging to {log_file_path}')

    local_logger = logging.getLogger('client-log')
    local_logger.setLevel(logging.DEBUG)
    
    # log to local text file
    #
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    local_logger.addHandler(file_handler)

    # add a console logger
    #
    console = logging.StreamHandler() 
    console.setLevel(logging.DEBUG)  
    console_log_formatter = logging.Formatter('local-sentry: %(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(console_log_formatter) 
    local_logger.addHandler(console) 

def random_id():
    return uuid.uuid4().hex

def id_rsp(id: str):
    return { 'id': id }

def project_endpoint(endpoint: Endpoint):
    return f'/api/{{project_id}}/{endpoint.value}/'

@api.get('/')
async def get_root():
    return f'local-sentry: {datetime.now().isoformat()}'

@api.post(project_endpoint(Endpoint.STORE))
async def store(request: Request):

    raw_body = await request.body()

    content_encoding = request.headers['content-encoding'] 
    content_type = request.headers['content-type']
    if content_encoding != 'deflate' or content_type !='application/octet-stream':
        raise Exception(f'unsupported content-encoding {content_encoding} and/or content-type {content_type}')

    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    inflated = decompress.decompress(raw_body[2:])
    inflated += decompress.flush()

    json_str = inflated.decode('ascii')
    event = json.loads(json_str)

    id = random_id()

    time_stamp = datetime.now().isoformat().replace(':', '-').replace('.', '_')

    event_msg = ''
    try:
        event_msg = event['message']
    except KeyError:
        pass

    file_name = f'{time_stamp} - {id} - {event_msg[:30]}.json'
    clean_file_name = file_name.replace('/', '|')
    file_path = os.path.join(log_file_folder_path, clean_file_name)

    with open(file_path, 'w') as dest_file:
        json.dump(event, dest_file)

    local_logger.info(f'/store len: {len(raw_body)} | id: {id} | {event_msg}')

    return id_rsp(id)

if __name__ == '__main__':
    
    print('local-sentry [LOCAL_SENTRY_LOG_FILE_FOLDER_PATH, LOCAL_SENTRY_PORT, LOCAL_SENTRY_LISTEN_HOST]')
    
    log_file_folder_path = os.environ.get('LOCAL_SENTRY_LOG_FILE_FOLDER_PATH', '/var/log/local-sentry')
    configure_logging(log_file_folder_path)
    
    try:
        port = int(os.environ.get('LOCAL_SENTRY_PORT', 9000))
        listen_host = os.environ.get('LOCAL_SENTRY_LISTEN_HOST', '0.0.0.0')
    except Exception:
        local_logger.exception('local-sentry: error retrieving environment variables')
        raise

    try:    
        local_logger.info(f'starting local-sentry server on {listen_host}:{port}')
        server = uvicorn.run(api, host=listen_host, port=port)
    except Exception:
        local_logger.exception('local-sentry server startup error')
        raise
