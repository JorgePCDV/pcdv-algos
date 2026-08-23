import numpy as np


def simulate_terminal_prices(
    spot: float,
    maturity: float,
    rate: float,
    volatility: float,
    n_simulations: int,
    seed: int | None = None,
) -> np.ndarray:
    if spot <= 0:
        raise ValueError("Spot price must be positive.")

    if maturity <= 0:
        raise ValueError("Maturity must be positive.")

    if volatility <= 0:
        raise ValueError("Volatility must be positive.")

    if n_simulations <= 0:
        raise ValueError("Number of simulations must be positive.")

    rng = np.random.default_rng(seed)

    z = rng.standard_normal(n_simulations)

    terminal_prices = spot * np.exp(
        (rate - 0.5 * volatility**2) * maturity
        + volatility * np.sqrt(maturity) * z
    )

    return terminal_prices