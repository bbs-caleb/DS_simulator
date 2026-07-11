"""Bank metrics implemented with method decorators."""

from __future__ import annotations

from typing import List


class BankMetrics:
    """Store bank accounts and calculate common banking metrics."""

    global_bank_rate: float = 15.0
    accounts: List[BankMetrics] = []

    def __init__(self, name: str, balance: float) -> None:
        self.name = name
        self.balance = balance
        BankMetrics.accounts.append(self)

    @staticmethod
    def adjust_global_bank_rate(new_rate: float) -> None:
        """Set a new interest rate for all bank accounts."""
        BankMetrics.global_bank_rate = new_rate

    @classmethod
    def calculate_avg_balance(cls) -> float:
        """Calculate the average balance across all created accounts."""
        total_balance = sum(account.balance for account in cls.accounts)
        return total_balance / len(cls.accounts)

    @classmethod
    def calculate_interest(
        cls,
        account: BankMetrics,
    ) -> float:
        """Calculate interest for a given bank account."""
        return account.balance * cls.global_bank_rate / 100


if __name__ == "__main__":
    account1 = BankMetrics("Tom", 15000)
    BankMetrics("Jerry", 20000)
    BankMetrics("Spike", 10000)

    assert BankMetrics.calculate_avg_balance() == 15000

    BankMetrics.adjust_global_bank_rate(16.0)
    assert BankMetrics.global_bank_rate == 16.0

    assert BankMetrics.calculate_interest(account1) == 2400.0
