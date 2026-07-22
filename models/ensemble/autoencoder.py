import torch
import torch.nn as nn
from typing import Dict, List, Any

class AutoencoderNet(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim)
        )
        
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

class AutoencoderAnomalyModel:
    def __init__(self, input_dim: int = 100):
        self._name = "autoencoder"
        self._version = "1.0.0"
        self.input_dim = input_dim
        self.model = AutoencoderNet(input_dim)
        self.threshold = 0.5
        
    @property
    def model_name(self) -> str:
        return self._name
        
    @property
    def model_version(self) -> str:
        return self._version
        
    def _pad_or_truncate(self, features: List[float]) -> torch.Tensor:
        if len(features) > self.input_dim:
            feats = features[:self.input_dim]
        else:
            feats = features + [0.0] * (self.input_dim - len(features))
        return torch.tensor(feats, dtype=torch.float32)

    def predict(self, features: Dict[str, float]) -> float:
        self.model.eval()
        with torch.no_grad():
            x = self._pad_or_truncate(list(features.values())).unsqueeze(0)
            reconstructed = self.model(x)
            mse = torch.mean((x - reconstructed)**2).item()
            prob = min(1.0, mse / self.threshold) if self.threshold > 0 else 0.5
            return prob
            
    def predict_batch(self, features: List[Dict[str, float]]) -> List[float]:
        self.model.eval()
        with torch.no_grad():
            xs = torch.stack([self._pad_or_truncate(list(f.values())) for f in features])
            reconstructed = self.model(xs)
            mses = torch.mean((xs - reconstructed)**2, dim=1)
            probs = torch.clamp(mses / self.threshold, max=1.0) if self.threshold > 0 else torch.full_like(mses, 0.5)
            return probs.tolist()
            
    def explain(self, features: Dict[str, float]) -> Dict[str, float]:
        return {}
        
    def train(self, X: Any, y: Any, **kwargs):
        pass
            
    def save(self, path: str):
        torch.save(self.model.state_dict(), path)
        
    def load(self, path: str):
        self.model.load_state_dict(torch.load(path))
