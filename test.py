import dotenv
import os
import certifi

from pymongo import *
from bson.objectid import ObjectId

dotenv.load_dotenv()

client = MongoClient(str(os.getenv("MON_STRING")), tlsCAFile=certifi.where())
db = client["CRBOT2Dat"]
warnsc = db["warns"]
print(warnsc.find_one(
    {
        "_id": ObjectId("000000000000000000010f2c")
    }
))