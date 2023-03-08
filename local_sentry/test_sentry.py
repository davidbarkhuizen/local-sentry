import requests
from datetime import datetime
import pytest
import uuid
import io
import json
import zlib

from .local_sentry import Endpoint

protocol = 'http'
public_key = 'public'
secret_key = 'secret_key'
local_loopback = '127.0.0.1'
host = '127.0.0.1'
port = 9000

project_id = 0

def format_dsn(
        protocol: str, 
        public_key: str, 
        secret_key: str,
        host: str,
        port: str,
        path: str,
        project_id: str):

    return f'{protocol}://{public_key}:{secret_key}@{host}:{port}/{path}/{project_id}'

def project_dsn(project_id: str):
    return format_dsn(protocol, public_key, secret_key, host, port, 'api', project_id)

def project_url(dsn: str, endpoint: Endpoint):
    return f'{dsn}/{endpoint.value}/'

def store(dsn: str, endpoint: Endpoint, payload_dict: dict | None = None):
    
    json_str = json.dumps(payload_dict)
    json_bytes = json_str.encode('ascii')
    print(json_bytes)

    compressor = zlib.compressobj(
        level=9, wbits=-zlib.MAX_WBITS, method=zlib.DEFLATED, memLevel=zlib.DEF_MEM_LEVEL, strategy=0)
    deflated = compressor.compress(json_bytes)
    deflated += compressor.flush()
    print(deflated)

    data = bytes([0, 0]) + deflated

    rsp = requests.post(project_url(dsn, endpoint), 
        headers={
            'content-encoding':'deflate',
            'content-type':'application/octet-stream'},  
        data=data)
    return rsp

@pytest.fixture
def sample_dsn():
    return project_dsn(project_id)

@pytest.fixture
def sample_store_payload():
    return {
        "A": "one",
        "B": "two",
        "C": "three",
        "timestamp": datetime.now().isoformat()
    }

def str_to_file(s: str):
    return io.StringIO(s)

def test_store(sample_dsn, sample_store_payload):
    rsp = store(sample_dsn, Endpoint.STORE, sample_store_payload)
    assert rsp.status_code == 200

def test_store_response_object_format(sample_dsn, sample_store_payload):
    rsp = store(sample_dsn, Endpoint.STORE, sample_store_payload)
    j = rsp.json()
    assert 'id' in j.keys()
    id = j['id']
    assert uuid.UUID(id).hex == id