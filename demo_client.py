\"\"\"Simple demo client to exercise endpoints locally.
Usage: set FIREBASE_CREDENTIALS_PATH if you want Firestore to be used.
Run the API: uvicorn main:app --reload
Then run: python demo_client.py
\"\"\"
import requests, os, json
base = os.getenv('TARA_BASE_URL', 'http://127.0.0.1:8000')
def post_expense_text():
    url = f'{base}/expense_buddy'
    data = {'user_id': 'demo_user', 'text': 'Bought diesel for ₹1500 from HP pump on Aug 3'}
    r = requests.post(url, data=data)
    print('expense_buddy:', r.status_code, r.text)
def post_mcp():
    url = f'{base}/mcp'
    payload = {'command': '/expense_buddy Bought diesel for ₹1200 from HP pump on Aug 4'}
    r = requests.post(url, json=payload, headers={'X-User-Phone': 'demo_user'})
    print('mcp:', r.status_code, r.text)
def get_metrics():
    r = requests.get(f'{base}/metrics')
    print('metrics:', r.status_code, r.text)
if __name__ == "__main__":
    post_expense_text()
    post_mcp()
    get_metrics()
