import torch
import torch.nn as nn
import torch.nn.functional as F
try:
    from torch_geometric.nn import SAGEConv
except ImportError:
    SAGEConv = None

class GraphSAGEFraudDetector(nn.Module):
    def __init__(self, in_channels: int, hidden_channels: int = 128, out_channels: int = 64):
        super().__init__()
        if SAGEConv is None:
            raise ImportError("torch_geometric is required for GraphSAGE")
            
        self.conv1 = SAGEConv(in_channels, hidden_channels, aggr='mean')
        self.conv2 = SAGEConv(hidden_channels, out_channels, aggr='mean')
        self.classifier = nn.Linear(out_channels, 1)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        
        out = self.classifier(x)
        return torch.sigmoid(out)
        
    def predict_node_risk(self, node_features, edge_index):
        self.eval()
        with torch.no_grad():
            return self.forward(node_features, edge_index)
