from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR,MODEL_FILE_NAME

import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
"""
this file does the following things:
It is a wrapper class which wraps both preprocessor and model together
During training it will be used to save both preprocessor and model in a single object
During inference it will be used to load both preprocessor and model in a single object

Holds the preprocessor
(standard scaler, one-hot encoder, power transformer, etc.)

 Holds the ML model
(RandomForest / XGBoost / Logistic Regression etc.)

During prediction
It automatically transforms the input using the same preprocessing pipeline used during training.
Then passes transformed data into the ML model.

Used for deployment
FastAPI / Flask will load this object and call .predict() directly.
"""
class NetworkModel:
    def __init__(self,preprocessor,model):
        try:
            self.preprocessor = preprocessor
            self.model = model
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def predict(self,x):
        try:
            x_transform = self.preprocessor.transform(x)
            y_hat = self.model.predict(x_transform)
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e,sys)