from __future__ import annotations

import torch
from torch import nn


class LSTMBaseline(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
        horizon: int,
        target_dim: int,
    ) -> None:
        super().__init__()
        effective_dropout = dropout if num_layers > 1 else 0.0
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=effective_dropout,
            batch_first=True,
        )
        self.head = nn.Linear(hidden_dim, horizon * target_dim)
        self.horizon = horizon
        self.target_dim = target_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, num_nodes, num_features = x.shape
        x = x.permute(0, 2, 1, 3).reshape(batch_size * num_nodes, seq_len, num_features)
        outputs, _ = self.lstm(x)
        last_hidden = outputs[:, -1, :]
        predictions = self.head(last_hidden)
        predictions = predictions.view(batch_size, num_nodes, self.horizon, self.target_dim)
        return predictions.permute(0, 2, 1, 3)
