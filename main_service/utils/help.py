import os
import hmac
from dotenv import load_dotenv,find_dotenv
import hashlib
import json

load_dotenv(find_dotenv())

def verify_webhook_signature(payload:str,signature:str)->bool:
    "verify webhook signature"
    secret = os.getenv("WEBHOOK_SECRET")
    expected_signature = f"sha256={hmac.new(secret.encode('utf-8'),payload.encode('utf-8'),hashlib.sha256).hexdigest()}"
    
    return hmac.compare_digest(expected_signature,signature)