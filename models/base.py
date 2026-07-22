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
        self._versions: Dict[str, str] = {}

    def register(self, model: FraudModel):
        self._models[model.model_name] = model
        self._versions[model.model_name] = model.model_version

    def get(self, name: str) -> FraudModel:
        if name not in self._models:
            raise KeyError(f"Model '{name}' not registered")
        return self._models[name]

    def list_models(self) -> List[str]:
        return list(self._models.keys())

    def get_model_info(self) -> List[Dict[str, str]]:
        return [{"name": name, "version": self._versions.get(name, "unknown")} for name in self._models]

    def load_all(self, directory: str):
        for name, model in self._models.items():
            model_path = os.path.join(directory, f"{name}.pkl")
            if os.path.exists(model_path):
                model.load(model_path)

    def reload(self, name: str, path: str):
        model = self.get(name)
        model.load(path)

    def register_defaults(self):
        from models.ensemble.xgboost_model import XGBoostFraudModel
        from models.ensemble.lightgbm_model import LightGBMFraudModel
        from models.ensemble.catboost_model import CatBoostFraudModel
        from models.ensemble.isolation_forest import IsolationForestModel
        self.register(XGBoostFraudModel())
        self.register(LightGBMFraudModel())
        self.register(CatBoostFraudModel())
        self.register(IsolationForestModel())
