from fastapi import APIRouter, Header, HTTPException, Body
from typing import Dict, Any
from services import firebase_client
from utils import parser
router = APIRouter(prefix='')
@router.get('/ping')
def ping():
    return {'status': 'mcp_endpoints ok'}
@router.post('/mcp')
async def mcp_endpoint(command: str = Body(...), x_puchai_key: str = Header(None), x_user_phone: str = Header(None)):
    # Very simple MCP handler: expects a text command string like:
    # "/expense_buddy Bought diesel for ₹1500 from HP pump on Aug 3"
    if not command:
        raise HTTPException(status_code=400, detail='command required in body')
    if command.strip().startswith('/expense_buddy'):
        text = command[len('/expense_buddy'):].strip()
        parsed = parser.parse_expense_from_text(text)
        user_id = x_user_phone or 'unknown_user'
        expense = {'user_id': user_id, 'vendor': parsed.get('vendor'), 'amount': parsed.get('amount'), 'date': parsed.get('date'), 'category': parsed.get('category'), 'raw_text': parsed.get('raw_text')}
        saved = firebase_client.save_expense(user_id, expense)
        firebase_client.increment_tool_usage('mcp_expense_buddy')
        return {'status': 'ok', 'expense': saved}
    return {'status': 'unsupported_command', 'command': command}
