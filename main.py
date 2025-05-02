from fastapi import FastAPI, Request from fastapi.middleware.cors import CORSMiddleware from pymongo import MongoClient from bson.json_util import dumps import re import os

from motor.motor_asyncio import AsyncIOMotorClient from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME

app = FastAPI()

Allow frontend access

app.add_middleware( CORSMiddleware, allow_origins=[""], allow_credentials=True, allow_methods=[""], allow_headers=["*"], )

MongoDB setup

client = AsyncIOMotorClient(DATABASE_URI) db = client[DATABASE_NAME] collection = db[COLLECTION_NAME]

@app.get("/search") async def search_files(q: str = ""): q = q.strip() if not q: raw_pattern = "." elif ' ' not in q: raw_pattern = r'(\b|[.-+])' + re.escape(q) + r'(\b|[.-+])' else: raw_pattern = re.sub(r'\s+', r'.*[\s.-_+]', re.escape(q))

try:
    regex = re.compile(raw_pattern, re.IGNORECASE)
except:
    return []

query = {"file_name": regex}
cursor = collection.find(query).sort("$natural", -1).limit(20)
files = await cursor.to_list(length=20)
# Select only needed fields
result = [{
    "file_id": f["file_id"],
    "file_name": f["file_name"],
    "file_size": f["file_size"]
} for f in files]
return result

