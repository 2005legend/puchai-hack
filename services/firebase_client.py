import os, threading, time
from typing import Dict, Any, List
# Try to init real firestore; otherwise fallback to in-memory.
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except Exception:
    FIREBASE_AVAILABLE = False
_lock = threading.Lock()
_in_memory = {
    "expenses": {},   # user_id -> list of expenses
    "bills": {},      # user_id -> list of bills
    "metrics": {},    # tool -> count
}
_db = None
def _init_firestore():
    """Initialize Firestore client if credentials are available."""
    global _db
    if _db is not None:
        return _db
    if not FIREBASE_AVAILABLE:
        return None
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH') or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not cred_path or not os.path.exists(cred_path):
        return None
    cred = credentials.Certificate(cred_path)
    project_id = os.getenv('FIREBASE_PROJECT_ID', None)
    try:
        if project_id:
            firebase_admin.initialize_app(cred, {'projectId': project_id})
        else:
            firebase_admin.initialize_app(cred)
    except Exception:
        # app may already be initialized
        pass
    _db = firestore.client()
    return _db


def save_expense(user_id: str, expense: Dict[str, Any]) -> Dict[str, Any]:
    """Save an expense to Firestore if available, otherwise to in-memory store. Returns saved object with id."""
    db = _init_firestore()
    if db:
        doc_ref = db.collection('expenses').document()
        expense['_id'] = doc_ref.id
        expense['created_at'] = int(time.time())
        doc_ref.set(expense)
        return expense
    # fallback
    with _lock:
        lst = _in_memory['expenses'].setdefault(user_id, [])
        expense = dict(expense)
        expense['_id'] = f"local-{len(lst)+1}"
        expense['created_at'] = int(time.time())
        lst.append(expense)
    return expense
def save_bill(user_id: str, bill: Dict[str, Any]) -> Dict[str, Any]:
    db = _init_firestore()
    if db:
        doc_ref = db.collection('bills').document()
        bill['_id'] = doc_ref.id
        bill['created_at'] = int(time.time())
        doc_ref.set(bill)
        return bill
    with _lock:
        lst = _in_memory['bills'].setdefault(user_id, [])
        bill = dict(bill)
        bill['_id'] = f"localbill-{len(lst)+1}"
        bill['created_at'] = int(time.time())
        lst.append(bill)
    return bill
def get_user_expenses(user_id: str) -> List[Dict[str, Any]]:
    db = _init_firestore()
    if db:
        docs = db.collection('expenses').where('user_id', '==', user_id).stream()
        return [d.to_dict() for d in docs]
    with _lock:
        return list(_in_memory['expenses'].get(user_id, []))
def increment_tool_usage(tool: str) -> None:
    db = _init_firestore()
    if db:
        metrics_ref = db.collection('metrics').document('usage')
        def tx_update(tx):
            snap = metrics_ref.get(transaction=tx)
            data = snap.to_dict() or {}
            data[tool] = data.get(tool, 0) + 1
            tx.set(metrics_ref, data)
        try:
            db.run_transaction(tx_update)
            return
        except Exception:
            pass
    with _lock:
        _in_memory['metrics'][tool] = _in_memory['metrics'].get(tool, 0) + 1
def get_metrics() -> Dict[str, int]:
    db = _init_firestore()
    if db:
        doc = db.collection('metrics').document('usage').get()
        return doc.to_dict() or {}
    with _lock:
        return dict(_in_memory['metrics'])
# Expose simple API
__all__ = ['save_expense', 'save_bill', 'get_user_expenses', 'increment_tool_usage', 'get_metrics']
