from dataclasses import dataclass

import numpy as np

from instruments.european_call import EuropeanCall
from monte_carlo.simulator import simulate_terminal_prices


@dataclass(frozen=True)
class MonteCarloResult:
    price: float
    standard_error: float
    confidence_interval: tuple[float, float]
    n_simulations: int


def price(
    instrument: EuropeanCall,
    n_simulations: int = 100_000,
    seed: int | None = None,
) -> MonteCarloResult:

    terminal_prices = simulate_terminal_prices(
        spot=instrument.spot,
        maturity=instrument.maturity,
        rate=instrument.rate,
        volatility=instrument.volatility,
        n_simulations=n_simulations,
        seed=seed,
    )

    payoffs = np.maximum(
        terminal_prices - instrument.strike,
        0.0,
    )

    discounted_payoffs = (
        np.exp(-instrument.rate * instrument.maturity)
        * payoffs
    )

    price_estimate = float(np.mean(discounted_payoffs))

    standard_error = float(
        np.std(discounted_payoffs, ddof=1)
        / np.sqrt(n_simulations)
    )

    margin = 1.96 * standard_error

    confidence_interval = (
        price_estimate - margin,
        price_estimate + margin,
    )

    return MonteCarloResult(
        price=price_estimate,
        standard_error=standard_error,
        confidence_interval=confidence_interval,
        n_simulations=n_simulations,
    )