"""Gated Residual Network (GRN) with Gated Linear Unit (GLU)."""
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

        x = self.elu_dense(x)            # eta_2 = ELU(W_2 * a + b_2)
        x = self.linear_dense(x)         # eta_1 = W_1 * eta_2 + b_1
        x = self.dropout(x)              # regularization after the linear layer
        x = self.glu(x)                  # GLU gating
        x = self.layer_norm(x + residual)  # residual + LayerNorm

        return x


def test() -> None:
    """Smoke test: check output shape for matching and non-matching input sizes."""
    torch.manual_seed(42)
    batch_size, hidden_size = 8, 16

    # Case 1: input_size == hidden_size (no projection)
    grn = GatedResidualNetwork(hidden_size, hidden_size, dropout_rate=0.1)
    out = grn(torch.randn(batch_size, hidden_size))
    assert out.shape == (batch_size, hidden_size)

    # Case 2: input_size != hidden_size (projection path)
    grn = GatedResidualNetwork(10, hidden_size, dropout_rate=0.1)
    out = grn(torch.randn(batch_size, 10))
    assert out.shape == (batch_size, hidden_size)

    print("All tests passed.")


if __name__ == "__main__":
    test()
