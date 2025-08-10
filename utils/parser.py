import re, io, os
from typing import Dict, Any
try:
    import pytesseract
    from PIL import Image, ImageOps, ImageFilter
    TESSERACT_AVAILABLE = True
except Exception:
    TESSERACT_AVAILABLE = False
import dateparser
rupee_pattern = re.compile(r'(?:(?:Rs\.?|INR|₹)\s?)([0-9,]+(?:\.[0-9]{1,2})?)', re.IGNORECASE)
amount_pattern_simple = re.compile(r'([0-9]+(?:\.[0-9]{1,2})?)')
date_search = lambda s: dateparser.search.search_dates(s, settings={'STRICT_PARSING': False}) if s else None
def ocr_image_bytes(image_bytes: bytes) -> str:
    if not TESSERACT_AVAILABLE:
        raise RuntimeError('pytesseract or PIL not available in this environment.')
    img = Image.open(io.BytesIO(image_bytes))
    # basic preprocess: convert to grayscale, enhance contrast
    img = ImageOps.grayscale(img)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    text = pytesseract.image_to_string(img)
    return text
def parse_receipt_from_text(text: str) -> Dict[str, Any]:
    """Extract vendor, date, amount, and a guessed category from OCR/text."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    vendor = lines[0] if lines else 'unknown'
    # Find amount by rupee symbol first
    amount = None
    m = rupee_pattern.search(text)
    if m:
        amt = m.group(1).replace(',', '')
        try:
            amount = float(amt)
        except:
            amount = None
    if amount is None:
        # fallback to last numeric-looking token
        ms = amount_pattern_simple.findall(text)
        if ms:
            try:
                amount = float(ms[-1])
            except:
                amount = None
    # Find date
    dates = date_search(text)
    date = dates[0][1].date().isoformat() if dates else None
    # Simple category heuristics
    cat = 'other'
    lowered = text.lower()
    if any(k in lowered for k in ['fuel', 'petrol', 'diesel', 'hp pump', 'petrol pump']):
        cat = 'fuel'
    elif any(k in lowered for k in ['electricity', 'bill', 'units', 'kwh']):
        cat = 'utilities'
    elif any(k in lowered for k in ['grocery', 'supermarket', 'store']):
        cat = 'grocery'
    return {
        'vendor': vendor,
        'amount': amount,
        'date': date,
        'category': cat,
        'raw_text': text
    }
def parse_receipt(image_bytes: bytes = None, text: str = None):
    if text is None and image_bytes is None:
        raise ValueError('Provide image bytes or text to parse_receipt')
    if text is None:
        text = ocr_image_bytes(image_bytes)
    return parse_receipt_from_text(text)
def parse_expense_from_text(text: str):
    # Text might be like: "Bought diesel for ₹1500 from HP pump on Aug 3"
    data = {}
    # Amount
    m = rupee_pattern.search(text)
    if m:
        try:
            data['amount'] = float(m.group(1).replace(',', ''))
        except:
            data['amount'] = None
    else:
        m2 = amount_pattern_simple.search(text)
        data['amount'] = float(m2.group(1)) if m2 else None
    # Date
    dates = date_search(text)
    data['date'] = dates[0][1].date().isoformat() if dates else None
    # Vendor - heuristic: "from X" or first capitalized words
    vendor = None
    fm = re.search(r'from\s+([A-Za-z0-9 &.-]+)', text, re.IGNORECASE)
    if fm:
        vendor = fm.group(1).strip()
    else:
        # use first line-ish content
        vendor = text.split(' for ')[-1].split(' on ')[0][:60].strip()
    data['vendor'] = vendor or 'unknown'
    # category heuristic
    lowered = text.lower()
    if 'diesel' in lowered or 'petrol' in lowered:
        cat = 'fuel'
    elif 'taxi' in lowered or 'cab' in lowered:
        cat = 'transport'
    else:
        cat = 'other'
    data['category'] = cat
    data['raw_text'] = text
    return data
__all__ = ['parse_receipt', 'parse_receipt_from_text', 'parse_expense_from_text']
