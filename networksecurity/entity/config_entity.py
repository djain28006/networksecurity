from datetime import datetime
import os,sys
from networksecurity.constant import training_pipeline
from networksecurity.exception import NetworkSecurityException
from networksecurity.logging import logger

class TrainingPipelineConfig:
    def __init__(self,timestamp=datetime.now()):
        try:
            timestamp=f"{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}"
            self.pipeline_name=training_pipeline.PIPELINE_NAME
            self.artifact_name=training_pipeline.ARTIFACT_NAME
            self.artifact_dir=os.path.join(self.artifact_name,timestamp)
            self.timestamp: str=timestamp
        except Exception as e:
            raise NetworkSecurityException(e,sys)


class DataIngestionConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        try:
            self.data_ingestion_dir = os.path.join(
                training_pipeline_config.artifact_dir,
                training_pipeline.DATA_INGESTION_DIR_NAME
            )

            # feature store path → directory + csv file
            self.feature_store_file_path = os.path.join(
                self.data_ingestion_dir,
                training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR,
                training_pipeline.FILE_NAME
            )

            # ingested directory
            self.ingested_dir = os.path.join(
                self.data_ingestion_dir,
                training_pipeline.DATA_INGESTION_INGESTED_DIR
            )

            # train + test paths inside ingested folder
            self.training_file_path = os.path.join(
                self.ingested_dir,
                training_pipeline.TRAIN_FILE_NAME
            )

            self.test_file_path = os.path.join(
                self.ingested_dir,
                training_pipeline.TEST_FILE_NAME
            )

            # ratio
            self.train_test_split_ratio = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO

            self.collection_name = training_pipeline.DATA_INGESTION_COLLECTION_NAME
            self.database_name = training_pipeline.DATA_INGESTION_DATABASE_NAME

        except Exception as e:
            raise NetworkSecurityException(e, sys)

            