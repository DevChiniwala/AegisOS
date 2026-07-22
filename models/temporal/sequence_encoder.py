import torch
import torch.nn as nn
import torch.nn.functional as F

class SequenceEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_size: int = 64, num_layers: int = 2):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_size, num_layers=num_layers, batch_first=True, bidirectional=True)
        self.attention = nn.Linear(hidden_size * 2, 1)
        
    def forward(self, x):
        out, _ = self.gru(x)
        
        attn_weights = F.softmax(self.attention(out), dim=1)
        attended_rep = torch.sum(out * attn_weights, dim=1)
        
        return attended_rep
