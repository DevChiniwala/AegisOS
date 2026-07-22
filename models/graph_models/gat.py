import torch
import torch.nn as nn
import torch.nn.functional as F
try:
    from torch_geometric.nn import GATConv
except ImportError:
    GATConv = None

class GATFraudDetector(nn.Module):
    def __init__(self, in_channels: int, hidden_channels: int = 64, heads: int = 8, out_channels: int = 64):
        super().__init__()
        if GATConv is None:
            raise ImportError("torch_geometric is required for GAT")
            
        self.conv1 = GATConv(in_channels, hidden_channels, heads=heads, concat=True)
        self.conv2 = GATConv(hidden_channels * heads, out_channels, heads=1, concat=False)
        self.classifier = nn.Linear(out_channels, 1)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.elu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        
        x = self.conv2(x, edge_index)
        x = F.elu(x)
        
        out = self.classifier(x)
        return torch.sigmoid(out)

    def get_attention_weights(self, x, edge_index):
        # Extract attention weights for explainability
        x, (edge_index_out, alpha) = self.conv1(x, edge_index, return_attention_weights=True)
        return edge_index_out, alpha
