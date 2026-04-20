from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
import os
import string
import secrets

IST = pytz.timezone('Asia/Kolkata')

class LicenseManager:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.hunter_bot
        self.licenses = self.db.licenses

    def generate_key(self):
        alphabet = string.ascii_uppercase + string.digits
        return 'HT-' + '-'.join(''.join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3))

    def create_license(self, nickname, duration_days):
        key = self.generate_key()
        expiry = datetime.now(IST) + timedelta(days=duration_days)
        
        self.licenses.insert_one({
            "key": key,
            "nickname": nickname,
            "duration_days": duration_days,
            "expires_at": expiry,
            "device_id": None,
            "status": "active",
            "created_at": datetime.now(IST)
        })
        return {
            "key": key,
            "nickname": nickname,
            "expires_at": expiry
        }

    def list_licenses(self, limit=10, skip=0):
        all_keys = list(self.licenses.find().sort("created_at", -1).skip(skip).limit(limit))
        now = datetime.now(IST)
        
        for lic in all_keys:
            expiry = lic.get("expires_at")
            if expiry:
                expiry_with_tz = expiry.replace(tzinfo=IST) if expiry.tzinfo is None else expiry
                if now > expiry_with_tz and lic.get("status") != "expired":
                    self.licenses.update_one({"_id": lic["_id"]}, {"$set": {"status": "expired"}})
                    lic["status"] = "expired"
        
        return all_keys

    def get_license(self, key):
        return self.licenses.find_one({"key": key})

    def extend_license(self, key, days):
        lic = self.get_license(key)
        if not lic:
            return None
            
        current_expiry = lic.get("expires_at")
        if current_expiry and current_expiry.tzinfo is None:
            current_expiry = IST.localize(current_expiry)
        elif not current_expiry:
            current_expiry = datetime.now(IST)
            
        now = datetime.now(IST)
        base_date = max(now, current_expiry)
        new_expiry = base_date + timedelta(days=days)
        
        self.licenses.update_one({"key": key}, {"$set": {
            "expires_at": new_expiry,
            "status": "active"
        }})
        return new_expiry

    def reset_device(self, key):
        result = self.licenses.update_one({"key": key}, {"$set": {"device_id": None}})
        return result.modified_count > 0

    def update_status(self, key, status):
        result = self.licenses.update_one({"key": key}, {"$set": {"status": status}})
        return result.modified_count > 0

    def delete_license(self, key):
        result = self.licenses.delete_one({"key": key})
        return result.deleted_count > 0
