from dataclasses import dataclass


@dataclass(frozen=True)
class EuropeanCall:
    spot: float
    strike: float
    maturity: float
    rate: float
    volatility: float

    def payoff(self, terminal_spot: float) -> float:
        return max(terminal_spot - self.strike, 0.0)