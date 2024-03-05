from pymongo import MongoClient
import os

url = os.environ.get('MONGO_SERVER_URL')

client = MongoClient(url)

db = client[
    'demodatabase'
]

COLLECTIONS = db.list_collection_names()