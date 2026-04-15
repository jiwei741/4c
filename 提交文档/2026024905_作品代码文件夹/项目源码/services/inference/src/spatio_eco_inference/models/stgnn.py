from __future__ import annotations

import torch
from torch import nn


def normalize_adjacency(adjacency: torch.Tensor) -> torch.Tensor:
    identity = torch.eye(adjacency.size(0), device=adjacency.device, dtype=adjacency.dtype)
    adjacency = adjacency + identity
    degree = adjacency.sum(dim=1)
    inv_sqrt_degree = torch.pow(degree.clamp(min=1e-6), -0.5)
    return inv_sqrt_degree[:, None] * adjacency * inv_sqrt_degree[None, :]


class GraphTemporalNet(nn.Module):
    def __init__(
        self,
        input_dim: int,
        graph_hidden_dim: int,
        temporal_hidden_dim: int,
        num_layers: int,
        dropout: float,
        horizon: int,
        target_dim: int,
        adjacency: torch.Tensor,
    ) -> None:
        super().__init__()
        self.register_buffer("adjacency", normalize_adjacency(adjacency))
        self.graph_linear = nn.Linear(input_dim, graph_hidden_dim)
        effective_dropout = dropout if num_layers > 1 else 0.0
        self.temporal = nn.LSTM(
            input_size=graph_hidden_dim,
            hidden_size=temporal_hidden_dim,
            num_layers=num_layers,
            dropout=effective_dropout,
            batch_first=True,
        )
        self.head = nn.Linear(temporal_hidden_dim, horizon * target_dim)
        self.activation = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.horizon = horizon
        self.target_dim = target_dim

    def graph_step(self, x_t: torch.Tensor) -> torch.Tensor:
        support = torch.einsum("ij,bjf->bif", self.adjacency, x_t)
        return self.activation(self.graph_linear(support))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, num_nodes, _ = x.shape
        graph_encoded = [self.graph_step(x[:, step]) for step in range(seq_len)]
        graph_encoded = torch.stack(graph_encoded, dim=1)
        graph_encoded = self.dropout(graph_encoded)
        graph_encoded = graph_encoded.permute(0, 2, 1, 3)
        graph_encoded = graph_encoded.reshape(batch_size * num_nodes, seq_len, -1)
        temporal_outputs, _ = self.temporal(graph_encoded)
        last_hidden = temporal_outputs[:, -1, :]
        predictions = self.head(last_hidden)
        predictions = predictions.view(batch_size, num_nodes, self.horizon, self.target_dim)
        return predictions.permute(0, 2, 1, 3)
