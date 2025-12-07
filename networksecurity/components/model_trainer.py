import os
import sys
import joblib

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact
)
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object, load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data, evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
import mlflow
import dagshub

# Initialize DagsHub MLflow
dagshub.init(repo_owner='djain28006', repo_name='networksecurity', mlflow=True)


class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig,
                 data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # --------------------------
    # MLflow Tracking (Fixed!)
    # --------------------------
    def track_mlflow(self, best_model, metric):
        with mlflow.start_run():

            # Log metrics
            mlflow.log_metric("f1_score", metric.f1_score)
            mlflow.log_metric("precision", metric.precision_score)
            mlflow.log_metric("recall_score", metric.recall_score)

            # Save model manually (supported by DagsHub)
            model_path = "best_model.pkl"
            joblib.dump(best_model, model_path)

            # Log artifact instead of mlflow.sklearn.log_model()
            mlflow.log_artifact(model_path)

            # Clean file
            os.remove(model_path)

    # --------------------------
    # Model Training Function
    # --------------------------
    def train_model(self, X_train, y_train, X_test, y_test):

        models = {
            "Random Forest": RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1),
            "AdaBoost": AdaBoostClassifier(),
        }

        params = {
            "Decision Tree": {
                'criterion': ['gini', 'entropy', 'log_loss'],
            },
            "Random Forest": {
                'n_estimators': [8, 16, 32, 128, 256]
            },
            "Gradient Boosting": {
                'learning_rate': [.1, .01, .05, .001],
                'subsample': [0.6, 0.7, 0.75, 0.85, 0.9],
                'n_estimators': [8, 16, 32, 64, 128, 256]
            },
            "Logistic Regression": {},
            "AdaBoost": {
                'learning_rate': [.1, .01, .001],
                'n_estimators': [8, 16, 32, 64, 128, 256]
            }
        }

        # Evaluate all models
        model_report: dict = evaluate_models(
            X_train=X_train, y_train=y_train,
            X_test=X_test, y_test=y_test,
            models=models, param=params
        )

        # Select best model
        best_model_score = max(model_report.values())
        best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]
        best_model = models[best_model_name]

        # Training metrics
        y_train_pred = best_model.predict(X_train)
        train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)

        # Log train metrics
        self.track_mlflow(best_model, train_metric)

        # Testing metrics
        y_test_pred = best_model.predict(X_test)
        test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)

        # Log test metrics
        self.track_mlflow(best_model, test_metric)

        # Save final combined model (preprocessor + model)
        preprocessor = load_object(
            file_path=self.data_transformation_artifact.transformed_object_file_path
        )

        model_dir = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir, exist_ok=True)

        final_model = NetworkModel(preprocessor=preprocessor, model=best_model)

        save_object(self.model_trainer_config.trained_model_file_path, obj=final_model)

        # Only model (for quick use)
        save_object("final_model/model.pkl", best_model)

        # Prepare artifact object
        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=train_metric,
            test_metric_artifact=test_metric
        )

        logging.info(f"Model trainer artifact: {model_trainer_artifact}")

        return model_trainer_artifact

    # --------------------------
    # Entry point
    # --------------------------
    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_path = self.data_transformation_artifact.transformed_train_file_path
            test_path = self.data_transformation_artifact.transformed_test_file_path

            train_arr = load_numpy_array_data(train_path)
            test_arr = load_numpy_array_data(test_path)

            X_train, y_train, X_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            return self.train_model(X_train, y_train, X_test, y_test)

        except Exception as e:
            raise NetworkSecurityException(e, sys)
