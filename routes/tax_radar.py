from fastapi import APIRouter, Query
from services import firebase_client
from datetime import datetime, timedelta, date
router = APIRouter(prefix='')
@router.get('/ping')
def ping():
    return {'status': 'tax_radar ok'}
@router.get('/tax_radar')
def tax_radar(user_id: str = Query(...)):
    # Compute simple metrics from last 90 days
    todos = firebase_client.get_user_expenses(user_id)
    cutoff = datetime.utcnow().date() - timedelta(days=90)
    recent = [t for t in todos if t.get('date') and t.get('date') >= cutoff.isoformat()]
    total = sum((t.get('amount') or 0) for t in recent)
    # crude estimate of income and tax
    est_income = total / 0.7 if total else 0
    est_tax = est_income * 0.04
    return {'status': 'ok', 'total_last_90_days': total, 'estimated_income': est_income, 'estimated_tax': est_tax, 'records_count': len(recent)}
