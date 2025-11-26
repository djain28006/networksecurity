from dataclasses import dataclass
from networksecurity.entity.config_entity import DataIngestionConfig

@dataclass
class DataIngestionArtifact:
    training_file_path: str
    test_file_path: str