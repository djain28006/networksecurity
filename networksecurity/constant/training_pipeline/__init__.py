import os
import sys
import numpy as np
import pandas as pd
from networksecurity.logging import logger
from networksecurity.exception import NetworkSecurityException

"""
defining the common variables for the training pipeline
"""

TARGET_COLUMN = "Result"

PIPELINE_NAME = "NetworkSecurity"

# Use a single consistent artifact folder name
ARTIFACT_NAME = "Artifacts"

FILE_NAME = "phisingData.csv"

TRAIN_FILE_NAME = "train.csv"
TEST_FILE_NAME = "test.csv"

"""
Data Ingestion related constants start with DATA_INGESTION_* 
"""

DATA_INGESTION_COLLECTION_NAME = "Network_Data"
DATA_INGESTION_DATABASE_NAME = "netsec"

DATA_INGESTION_DIR_NAME = "data_ingestion"

DATA_INGESTION_FEATURE_STORE_DIR = "feature_store"
DATA_INGESTION_INGESTED_DIR = "ingested"

# Correct spelling
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO = 0.20

SCHEMA_FILE_PATH = os.path.join("data_schema","schema.yaml")

"""
Data Validation related constants start with DATA_VALIDATION VAR NAME
"""
DATA_VALIDATION_DIR_NAME = "data_validation"
DATA_VALIDATION_VALID_DIR = "validated"
DATA_VALIDATION_INVALID_DIR = "invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME = "report.yaml"

