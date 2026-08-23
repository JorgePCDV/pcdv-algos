from src.pricing.instruments.european_call import EuropeanCall
from src.pricing.models.black_scholes import call_price


def delta(
        instrument: EuropeanCall,
        bump: float = 0.01,
) -> float:
    up = EuropeanCall(
        spot=instrument.spot + bump,
        strike=instrument.strike,
        maturity=instrument.maturity,
        rate=instrument.rate,
        volatility=instrument.volatility,
    )

    down = EuropeanCall(
        spot=instrument.spot - bump,
        strike=instrument.strike,
        maturity=instrument.maturity,
        rate=instrument.rate,
        volatility=instrument.volatility,
    )

    return (
            call_price(
                up.spot,
                up.strike,
                up.maturity,
                up.rate,
                up.volatility,
            )
            -
            call_price(
                down.spot,
                down.strike,
                down.maturity,
                down.rate,
                down.volatility,
            )
    ) / (2 * bump)


def gamma(
        instrument: EuropeanCall,
        bump: float = 0.01,
) -> float:
    base = call_price(
        instrument.spot,
        instrument.strike,
        instrument.maturity,
        instrument.rate,
        instrument.volatility,
    )

    up = call_price(
        instrument.spot + bump,
        instrument.strike,
        instrument.maturity,
        instrument.rate,
        instrument.volatility,
    )

    down = call_price(
        instrument.spot - bump,
        instrument.strike,
        instrument.maturity,
        instrument.rate,
        instrument.volatility,
    )

    return (up - 2 * base + down) / bump ** 2


def vega(
        instrument: EuropeanCall,
        bump: float = 0.0001,
) -> float:
    up = call_price(
        instrument.spot,
        instrument.strike,
        instrument.maturity,
        instrument.rate,
        instrument.volatility + bump,
    )

    down = call_price(
        instrument.spot,
        instrument.strike,
        instrument.maturity,
        instrument.rate,
        instrument.volatility - bump,
    )

    return (up - down) / (2 * bump)


def rho(
        instrument: EuropeanCall,
        bump: float = 0.0001,
) -> float:
    up = call_price(
        instrument.spot,
        instrument.strike,
        instrument.maturity,
        instrument.rate + bump,
        instrument.volatility,
    )

    down = call_price(
        instrument.spot,
        instrument.strike,
        instrument.maturity,
        instrument.rate - bump,
        instrument.volatility,
    )

    return (up - down) / (2 * bump)
