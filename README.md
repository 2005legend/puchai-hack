# TARA Integrated Project (Firestore + OCR)

This is the fully integrated **AI-powered expense & bill management API**.

## Features
- **Bill Scanner**: Upload receipts/bills → OCR → auto-extract vendor, date, amount, category → save to Firestore.
- **Expense Buddy**: Log expenses via text or JSON.
- **MCP Endpoint**: Integrate with Puch AI commands.
- **Analytics**: Track endpoint usage.
- **Tax Radar**: Calculate recent expenses and estimate tax.

## Requirements
- Python 3.10+
- Tesseract OCR installed on your system (optional but required for OCR from images)
- Firebase Firestore project (already integrated with `serviceAccountKey.json`)

## Setup

1. **Clone/Unzip Project**
   ```bash
   unzip TARA_Integrated_ready.zip
   cd TARA_Integrated_final
   ```

2. **Create Virtual Environment & Install Dependencies**
   ```bash
   python -m venv venv
   # Linux/macOS
   source venv/bin/activate
   # Windows
   venv\Scripts\activate

   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file or edit the provided one:
   ```env
   FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
   FIREBASE_PROJECT_ID=puch-ai-hackathon-final
   PUCHAI_APP_KEY=your_puchai_key_here
   ```

4. **Run the API**
   ```bash
   uvicorn main:app --reload
   ```

5. **Access API Docs**
   Open: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Endpoints

### Bill Scanner
- **POST /bill_scanner_upload**
  - Form fields: `user_id`, `file` (image file)
- **POST /bill_scanner**
  - Form fields: `user_id`, `parsed_json` (JSON string)

### Expense Buddy
- **POST /expense_buddy**
  - Form fields: `user_id`, `text` (free text) **or** JSON body

### MCP Endpoint
- **POST /mcp**
  - JSON body: `{ "command": "/expense_buddy Bought diesel for ₹1500 from HP pump on Aug 3" }`
  - Header: `X-User-Phone` (used as `user_id`)

### Analytics
- **GET /metrics**

### Tax Radar
- **GET /tax_radar?user_id=demo_user**

## Demo
Run the included demo client:
```bash
python demo_client.py
```

## OCR Setup Notes
- Install Tesseract:
  - **Windows**: [Download here](https://github.com/UB-Mannheim/tesseract/wiki)
  - **Linux**: `sudo apt install tesseract-ocr`
  - **macOS**: `brew install tesseract`
- Set Tesseract path in code if needed:
  ```python
  import pytesseract
  pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```
