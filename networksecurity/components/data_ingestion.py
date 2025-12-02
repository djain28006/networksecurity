import os,sys
import pandas as pd
import numpy as np
import pymongo
from networksecurity.logging.logger import logging
from networksecurity.exception import NetworkSecurityException
from networksecurity.entity.artifact_entity import DataIngestionArtifact

# configuration of data ingestion configuration
from networksecurity.entity.config_entity import DataIngestionConfig
from typing import List
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv
load_dotenv()
MONGO_DB_URL=os.getenv("MONGO_DB_URL")  
# get the mongodb url from the .env file

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def export_collection_as_dataframe(self):
        '''
        Read data from MongoDB collection and convert it into pandas dataframe
        1. Read the collection name and database name from the data ingestion config
        2. Use pymongo to read the data from the collection
        3. Convert the data into pandas dataframe
        4. Replace "na" values with np.NAN
        '''
        try:
            database_name=self.data_ingestion_config.database_name
            collection_name=self.data_ingestion_config.collection_name
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            collection=self.mongo_client[database_name][collection_name]
            df=pd.DataFrame(list(collection.find()))
            if "_id" in df.columns:
                df=df.drop(columns=["_id"],axis=1)
            df.replace(to_replace="na", value=np.nan, inplace=True)
            return df
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
            
    def export_data_into_feature_store(self,dataframe):
        try:
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            # creating folder
            dir_path=os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e,sys)
            
    def split_data_as_train_test(self,dataframe):    
        try:
            train_set,test_set=train_test_split(dataframe,test_size=self.data_ingestion_config.train_test_split_ratio,random_state=42)
            logging.info("Performed train test split")
            logging.info("Exited split_data_as_train_test method of Data Ingestion class")
            dir_path=os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path,exist_ok=True)
            logging.info("Created directory for train and test data")
            train_set.to_csv(self.data_ingestion_config.training_file_path,index=False,header=True)
            test_set.to_csv(self.data_ingestion_config.test_file_path,index=False,header=True)
            logging.info("Saved train and test data")    
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        

    def initiate_data_ingestion(self):
        try:
            dataframe=self.export_collection_as_dataframe()
            dataframe=self.export_data_into_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            dataingestionartifact = DataIngestionArtifact(
            training_file_path=self.data_ingestion_config.training_file_path,
            test_file_path=self.data_ingestion_config.test_file_path
            )

            return dataingestionartifact

        except Exception as e:
            raise NetworkSecurityException(e,sys)