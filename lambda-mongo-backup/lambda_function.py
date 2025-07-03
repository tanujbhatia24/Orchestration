# lambda_function.py
import pymongo
import boto3
import os
import json
from datetime import datetime

def lambda_handler(event, context):
    mongo_uri = os.environ['MONGO_URI']
    db_name = os.environ['DB_NAME']
    collection_name = os.environ['COLLECTION_NAME']
    bucket_name = os.environ['BUCKET_NAME']

    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    data = list(collection.find({}))

    s3 = boto3.client('s3')
    backup_file = f"{collection_name}-{datetime.utcnow().isoformat()}.json"

    s3.put_object(
        Bucket=bucket_name,
        Key=backup_file,
        Body=json.dumps(data, default=str).encode('utf-8')
    )

    return {"message": "Backup uploaded", "file": backup_file}
