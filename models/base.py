from typing import Protocol, Dict, List, Any
import os

class FraudModel(Protocol):
    @property
    def model_name(self) -> str:
        ...
        
    @property
    def model_version(self) -> str:
        ...
        
    def predict(self, features: Dict[str, float]) -> float:
        ...
        
    def predict_batch(self, features: List[Dict[str, float]]) -> List[float]:
        ...
        
    def explain(self, features: Dict[str, float]) -> Dict[str, float]:
        ...
        
    def train(self, X: Any, y: Any, **kwargs):
        ...
        
    def save(self, path: str):
        ...
        
    def load(self, path: str):
        ...

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, FraudModel] = {}
        
    def register(self, model: FraudModel):
        self._models[model.model_name] = model
        
    def get(self, name: str) -> FraudModel:
        return self._models[name]
        
    def list_models(self) -> List[str]:
        return list(self._models.keys())
        
    def load_all(self, directory: str):
        pass
