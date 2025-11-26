import os,sys,json
from typing import Collection

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

import certifi
ca=certifi.where()
# certify is used to verify the certificate of the server and it is used to connect to the server
# in simple words it is used to connect to the server and it is used to insert the data into the database

import numpy as np
import pandas as pd
import pymongo
from networksecurity.logging import logger
from networksecurity.exception import NetworkSecurityException

class NetworkDataExtract:
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def cv_to_json(self,cv_path):
        try:
            data=pd.read_csv(cv_path)
            data.reset_index(drop=True,inplace=True)
            records=list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def insert_data_to_mongodb(self,records,database,collection):
        try:
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL,tlsCAFile=ca)
            db=self.mongo_client[database]
            collection_handle=db[collection]
            collection_handle.insert_many(records)
            return len(records)
        except Exception as e:
            raise NetworkSecurityException(e,sys)


if __name__=="__main__":
    try:
        FILE_PATH="Network_Data\phisingData.csv"
        DATABASE="netsec"
        Collection="Network_Data"
        networkobj=NetworkDataExtract()
        records=networkobj.cv_to_json(FILE_PATH)
        no_of_records=networkobj.insert_data_to_mongodb(records,DATABASE,Collection)
        print(f"Number of records inserted: {no_of_records}")
        print(f"records inserted: {records}")

    except Exception as e:
        print(e)
