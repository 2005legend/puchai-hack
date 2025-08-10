from fastapi import APIRouter, Form, HTTPException, Body
from typing import Dict, Any
from services import firebase_client
from utils import parser
router = APIRouter(prefix='')
@router.get('/ping')
def ping():
    return {'status': 'expense_buddy ok'}
@router.post('/expense_buddy')
async def expense_buddy_text(user_id: str = Form(...), text: str = Form(None), payload: Dict[str,Any] = Body(None)):
    # Accept either text form or JSON body payload
    if payload:
        # expected keys: vendor, amount, date, category
        data = dict(payload)
    elif text:
        data = parser.parse_expense_from_text(text)
    else:
        raise HTTPException(status_code=400, detail='Provide text form or JSON body')
    expense = {'user_id': user_id, 'vendor': data.get('vendor'), 'amount': data.get('amount'), 'date': data.get('date'), 'category': data.get('category'), 'raw_text': data.get('raw_text')}
    saved = firebase_client.save_expense(user_id, expense)
    firebase_client.increment_tool_usage('expense_buddy')
    return {'status': 'ok', 'expense': saved}
