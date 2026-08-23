import math
from statistics import NormalDist


NORMAL = NormalDist()


def _validate_inputs(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> None:
    if spot <= 0:
        raise ValueError("Spot price must be positive.")

    if strike <= 0:
        raise ValueError("Strike price must be positive.")

    if maturity <= 0:
        raise ValueError("Maturity must be positive.")

    if volatility <= 0:
        raise ValueError("Volatility must be positive.")


def d1(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    _validate_inputs(spot, strike, maturity, rate, volatility)

    return (
        math.log(spot / strike)
        + (rate + 0.5 * volatility**2) * maturity
    ) / (volatility * math.sqrt(maturity))


def d2(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    d1_value = d1(
        spot,
        strike,
        maturity,
        rate,
        volatility,
    )

    return d1_value - volatility * math.sqrt(maturity)


def call_price(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    volatility: float,
) -> float:
    d1_value = d1(
        spot,
        strike,
        maturity,
        rate,
        volatility,
    )

    d2_value = d2(
        spot,
        strike,
        maturity,
        rate,
        volatility,
    )

    return (
        spot * NORMAL.cdf(d1_value)
        - strike
        * math.exp(-rate * maturity)
        * NORMAL.cdf(d2_value)
    )