"""Variable Selection Network (VSN) built on Gated Residual Networks."""
from typing import List

import torch
from torch import nn


class GatedLinearUnit(nn.Module):
    """
    Gated Linear Unit implementation.

    Args:
        input_size (int): Size of input features
        output_size (int): Size of output features

    Returns:
        torch.Tensor: Output tensor after applying GLU
    """

    def __init__(self, input_size, output_size):
        super().__init__()
        self.linear = nn.Linear(input_size, output_size)
        self.sigmoid = nn.Linear(input_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the GLU.

        Args:
            x (torch.Tensor): Input tensor

        Returns:
            torch.Tensor: Result of linear transformation multiplied by sigmoid gate
        """
        return self.linear(x) * torch.sigmoid(self.sigmoid(x))


class GatedResidualNetwork(nn.Module):
    """
    Gated Residual Network implementation.

    Args:
        input_size (int): Size of input features
        hidden_size (int): Size of hidden layer
        dropout_rate (float): Dropout rate for regularization

    Returns:
        torch.Tensor: Output tensor after processing through GRN
    """

    def __init__(self, input_size, hidden_size, dropout_rate):
        super().__init__()

        self.hidden_size = hidden_size

        self.elu_dense = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ELU()
        )

        self.linear_dense = nn.Linear(hidden_size, hidden_size)
        self.dropout = nn.Dropout(dropout_rate)
        self.glu = GatedLinearUnit(hidden_size, hidden_size)
        self.layer_norm = nn.LayerNorm(hidden_size)

        self.project = nn.Linear(input_size, hidden_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the GRN.

        Args:
            x (torch.Tensor): Input tensor

        Returns:
            torch.Tensor: Processed tensor
        """
        if x.shape[-1] != self.hidden_size:
            residual = self.project(x)
        else:
            residual = x

        x = self.elu_dense(x)
        x = self.linear_dense(x)
        x = self.dropout(x)
        x = self.glu(x)
        x = x + residual
        x = self.layer_norm(x)

        return x


class VariableSelection(nn.Module):
    """
    Variable Selection Network using Gated Residual Networks.

    Args:
        input_size (int): Size of input features
        hidden_size (int): Size of hidden layer
        dropout_rate (float): Dropout rate for regularization

    Returns:
        torch.Tensor: Weighted combination of processed features
    """

    def __init__(self, input_size: int, hidden_size: int, dropout_rate: float) -> None:
        super().__init__()
        self.num_features = input_size  # number of input features
        self.grns = nn.ModuleList()

        # Create a GRN for each feature independently
        for _ in range(self.num_features):
            grn = GatedResidualNetwork(hidden_size, hidden_size, dropout_rate)
            self.grns.append(grn)

        # Create a GRN for the concatenation of all the features
        self.grn_concat = GatedResidualNetwork(hidden_size * self.num_features,
                                               hidden_size,
                                               dropout_rate)
        self.softmax = nn.Linear(hidden_size, self.num_features)

    def forward(self, inputs: List[torch.Tensor]) -> torch.Tensor:
        """
        Forward pass of the Variable Selection Network.

        Args:
            inputs (List[torch.Tensor]): List of input feature tensors

        Returns:
            torch.Tensor: Weighted combination of processed features
        """
        # Concatenated inputs for features weights
        v = torch.cat(inputs, dim=-1)

        # Feature importance weights via concat-GRN + softmax
        v = self.grn_concat(v)              # (batch, hidden_size)
        v = self.softmax(v)                 # (batch, num_features)
        v = torch.softmax(v, dim=-1)        # normalized weights
        v = v.unsqueeze(-1)                 # (batch, num_features, 1)

        # Add GRN for each feature
        x = []
        for idx, feature in enumerate(inputs):
            x.append(self.grns[idx](feature))  # (batch, hidden_size)

        x = torch.stack(x, dim=1)           # (batch, num_features, hidden_size)

        # Compute weighted sum
        result = torch.matmul(v.transpose(-2, -1), x).squeeze(1)
        return result


def test() -> None:
    """Smoke test: output must be (batch_size, hidden_size)."""
    torch.manual_seed(42)
    batch_size, hidden_size, num_features = 8, 16, 5

    model = VariableSelection(num_features, hidden_size, dropout_rate=0.1)
    inputs = [torch.randn(batch_size, hidden_size) for _ in range(num_features)]

    result = model(inputs)
    assert result.shape == (batch_size, hidden_size)
    print("All tests passed.")


if __name__ == "__main__":
    test()
