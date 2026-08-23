import math

from src.pricing.instruments.european_call import EuropeanCall
from src.pricing.models.black_scholes import call_price
from src.pricing.monte_carlo.pricer import price


def test_black_scholes_price():
    option = EuropeanCall(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        volatility=0.20,
    )

    result = call_price(
        option.spot,
        option.strike,
        option.maturity,
        option.rate,
        option.volatility,
    )

    assert math.isclose(
        result,
        10.4506,
        rel_tol=1e-4,
    )


def test_monte_carlo_matches_black_scholes():
    option = EuropeanCall(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        volatility=0.20,
    )

    analytical_price = call_price(
        option.spot,
        option.strike,
        option.maturity,
        option.rate,
        option.volatility,
    )

    result = price(
        option,
        n_simulations=1_000_000,
        seed=42,
    )

    low, high = result.confidence_interval

    assert low <= analytical_price <= high


def test_payoff():
    option = EuropeanCall(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        volatility=0.20,
    )

    assert option.payoff(120.0) == 20.0
    assert option.payoff(80.0) == 0.0
