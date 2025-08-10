from fastapi import APIRouter
from services import firebase_client
router = APIRouter(prefix='')
@router.get('/ping')
def ping():
    return {'status': 'analytics ok'}
@router.get('/metrics')
def metrics():
    return {'status': 'ok', 'metrics': firebase_client.get_metrics()}
