import torch
import torch.nn as nn

class TemporalGraphNetwork(nn.Module):
    """
    Simplified Temporal Graph Network for Node Memory updates.
    """
    def __init__(self, num_nodes: int, memory_dim: int = 100, edge_feat_dim: int = 50):
        super().__init__()
        self.num_nodes = num_nodes
        self.memory_dim = memory_dim
        
        # Memory per node
        self.register_buffer('memory', torch.zeros(num_nodes, memory_dim))
        
        # Memory updater (GRU)
        self.memory_updater = nn.GRUCell(edge_feat_dim, memory_dim)

    def update_memory(self, source_id: int, target_id: int, timestamp: float, edge_features: torch.Tensor):
        """
        Update the memory of source and target nodes based on interaction.
        """
        # Ensure 2D tensor for GRU cell
        if edge_features.dim() == 1:
            edge_features = edge_features.unsqueeze(0)
            
        src_mem = self.memory[source_id].unsqueeze(0)
        tgt_mem = self.memory[target_id].unsqueeze(0)
        
        # Update source
        new_src_mem = self.memory_updater(edge_features, src_mem)
        self.memory[source_id] = new_src_mem.squeeze(0)
        
        # Update target
        new_tgt_mem = self.memory_updater(edge_features, tgt_mem)
        self.memory[target_id] = new_tgt_mem.squeeze(0)

    def compute_embedding(self, node_id: int) -> torch.Tensor:
        """
        Get the current temporal embedding for a node.
        """
        return self.memory[node_id]
