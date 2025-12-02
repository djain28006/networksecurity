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
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_columns_and_types(self, dataframe: pd.DataFrame) -> bool:
        """
        Validate both column names and numerical types according to schema
        """
        try:
            # Extract column names and types from schema
            schema_cols = [list(col.keys())[0] for col in self._schema_config['columns']]
            schema_types = {list(col.keys())[0]: list(col.values())[0] for col in self._schema_config['columns']}

            logging.info(f"Schema columns: {schema_cols}")
            logging.info(f"DataFrame columns: {list(dataframe.columns)}")

            # Check column names
            if list(dataframe.columns) != schema_cols:
                return False

            # Check numerical types
            for col, expected_type in schema_types.items():
                if col not in dataframe.columns:
                    return False
                actual_type = str(dataframe[col].dtype)
                if actual_type != expected_type:
                    logging.info(f"Column {col} has type {actual_type}, expected {expected_type}")
                    return False

            return True

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold=0.05) -> bool:
        """
        Detect drift using KS test. Returns True if no drift, False if drift detected.
        """
        try:
            status = True
            report = {}

            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]

                ks_result = ks_2samp(d1, d2)
                drift_found = ks_result.pvalue < threshold

                if drift_found:
                    status = False

                report[column] = {
                    "p_value": float(ks_result.pvalue),
                    "drift_status": drift_found
                }

            # Save drift report
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_file_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            # Load data
            train_df = self.read_data(self.data_ingestion_artifact.training_file_path)
            test_df = self.read_data(self.data_ingestion_artifact.test_file_path)

            # Validate columns and types
            train_valid = self.validate_columns_and_types(train_df)
            test_valid = self.validate_columns_and_types(test_df)

            if not train_valid or not test_valid:
                logging.info("Column or type validation failed. Moving data to invalid folder.")
                return DataValidationArtifact(
                    validation_status=False,
                    valid_train_file_path=None,
                    valid_test_file_path=None,
                    invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
                    invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                    drift_report_file_path=self.data_validation_config.drift_report_file_path,
                )

            # Detect dataset drift
            drift_status = self.detect_dataset_drift(train_df, test_df)

            # Save validated data
            os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)
            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False)

            logging.info("Data validation passed. Saving validated data.")

            return DataValidationArtifact(
                validation_status=drift_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)