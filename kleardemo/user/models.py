from django.db import models

from db_connection import db, COLLECTIONS

# Create your models here.

USER_COLLECTION = db.create_collection("User") if "User" not in COLLECTIONS else db["User"]
ADDRESS_COLLECTION = db.create_collection("Address") if "Address" not in COLLECTIONS else db["Address"]
WALLET_COLLECTION = db.create_collection("Wallet") if "Wallet" not in COLLECTIONS else db["Wallet"]