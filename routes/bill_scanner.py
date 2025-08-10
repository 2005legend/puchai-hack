from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Any, Dict
from services import firebase_client
from utils import parser
router = APIRouter(prefix='')
@router.get('/ping')
def ping():
    return {'status': 'bill_scanner ok'}
@router.post('/bill_scanner_upload')
async def bill_scanner_upload(user_id: str = Form(...), file: UploadFile = File(...)):
    contents = await file.read()
    try:
        parsed = parser.parse_receipt(image_bytes=contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'OCR failed: {e}')
    bill = {
        'user_id': user_id,
        'vendor': parsed.get('vendor'),
        'amount': parsed.get('amount'),
        'date': parsed.get('date'),
        'category': parsed.get('category'),
        'raw_text': parsed.get('raw_text'),
        'filename': file.filename
    }
    saved = firebase_client.save_bill(user_id, bill)
    firebase_client.increment_tool_usage('bill_scanner_upload')
    return {'status': 'ok', 'bill': saved}
@router.post('/bill_scanner')
async def bill_scanner(user_id: str = Form(...), parsed_json: str = Form(...)):
    # Accept already parsed JSON string
    import json
    try:
        parsed = json.loads(parsed_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail='parsed_json must be valid JSON string')
    bill = {'user_id': user_id, **parsed}
    saved = firebase_client.save_bill(user_id, bill)
    firebase_client.increment_tool_usage('bill_scanner')
    return {'status': 'ok', 'bill': saved}
