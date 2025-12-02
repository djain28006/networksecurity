from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH

from scipy.stats import ks_2samp
import pandas as pd
import os, sys
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file


class DataValidation:

    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):

        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.config = data_validation_config
            self.schema = read_yaml_file(SCHEMA_FILE_PATH)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        """Simple CSV loader"""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_columns(self, df: pd.DataFrame) -> bool:
        """
        Validate number of columns match with schema.yaml
        """
        try:
            required_columns = list(self.schema.keys())
            logging.info(f"Schema Columns: {required_columns}")
            logging.info(f"Data Columns: {list(df.columns)}")

            return len(df.columns) == len(required_columns)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame) -> bool:
        """
        Detect drift using KS-Test and save report.
        """
        try:
            drift_status = True
            drift_report = {}

            for column in base_df.columns:
                ks_result = ks_2samp(base_df[column], current_df[column])
                p_value = float(ks_result.pvalue)
                drift_found = p_value < 0.05

                if drift_found:
                    drift_status = False

                drift_report[column] = {
                    "p_value": p_value,
                    "drift_status": drift_found
                }

            # Save Drift Report
            os.makedirs(os.path.dirname(self.config.drift_report_file_path), exist_ok=True)
            write_yaml_file(self.config.drift_report_file_path, drift_report)

            return drift_status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_df = self.read_data(self.data_ingestion_artifact.training_file_path)
            test_df = self.read_data(self.data_ingestion_artifact.test_file_path)

            # Column Validation
            if not (self.validate_columns(train_df) and self.validate_columns(test_df)):
                logging.info("Column mismatch between schema and dataset")
                return DataValidationArtifact(
                    validation_status=False,
                    valid_train_file_path=None,
                    valid_test_file_path=None,
                    invalid_train_file_path=self.config.invalid_train_file_path,
                    invalid_test_file_path=self.config.invalid_test_file_path,
                    drift_report_file_path=self.config.drift_report_file_path,
                )

            # Drift Detection
            drift_status = self.detect_dataset_drift(train_df, test_df)

            # Save Validated Files
            os.makedirs(os.path.dirname(self.config.valid_train_file_path), exist_ok=True)

            train_df.to_csv(self.config.valid_train_file_path, index=False)
            test_df.to_csv(self.config.valid_test_file_path, index=False)

            # Create Artifact
            artifact = DataValidationArtifact(
                validation_status=drift_status,
                valid_train_file_path=self.config.valid_train_file_path,
                valid_test_file_path=self.config.valid_test_file_path,
                invalid_train_file_path=self.config.invalid_train_file_path,
                invalid_test_file_path=self.config.invalid_test_file_path,
                drift_report_file_path=self.config.drift_report_file_path,
            )

            logging.info(f"Data Validation Artifact: {artifact}")
            return artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
