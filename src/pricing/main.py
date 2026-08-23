import argparse

from instruments.european_call import EuropeanCall
from models.black_scholes import call_price
from monte_carlo.pricer import price
from risk.greeks import delta, gamma, vega, rho


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="European Call Option Pricing"
    )

    parser.add_argument(
        "--spot",
        type=float,
        required=True,
        help="Current underlying price"
    )

    parser.add_argument(
        "--strike",
        type=float,
        required=True,
        help="Option strike price"
    )

    parser.add_argument(
        "--maturity",
        type=float,
        required=True,
        help="Time to maturity in years"
    )

    parser.add_argument(
        "--rate",
        type=float,
        required=True,
        help="Risk-free interest rate as decimal, e.g. 0.05"
    )

    parser.add_argument(
        "--volatility",
        type=float,
        required=True,
        help="Volatility as decimal, e.g. 0.20"
    )

    parser.add_argument(
        "--simulations",
        type=int,
        default=1_000_000,
        help="Number of Monte Carlo simulations"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random number generator seed"
    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    option = EuropeanCall(
        spot=args.spot,
        strike=args.strike,
        maturity=args.maturity,
        rate=args.rate,
        volatility=args.volatility,
    )

    analytical = call_price(
        option.spot,
        option.strike,
        option.maturity,
        option.rate,
        option.volatility,
    )

    monte_carlo = price(
        option,
        n_simulations=args.simulations,
        seed=args.seed,
    )

    print()
    print("===================================")
    print("       EUROPEAN CALL OPTION")
    print("===================================")

    print()
    print("Market Parameters")
    print("-----------------")

    print(f"Spot:              {option.spot:.4f}")
    print(f"Strike:            {option.strike:.4f}")
    print(f"Maturity:          {option.maturity:.4f} years")
    print(f"Risk-free rate:    {option.rate:.2%}")
    print(f"Volatility:        {option.volatility:.2%}")

    print()
    print("Pricing")
    print("-------")

    print(f"Black-Scholes:     {analytical:.6f}")
    print(f"Monte Carlo:       {monte_carlo.price:.6f}")

    print()
    print("Monte Carlo Statistics")
    print("----------------------")

    print(f"Simulations:       {monte_carlo.n_simulations:,}")
    print(f"Standard error:    {monte_carlo.standard_error:.6f}")

    low, high = monte_carlo.confidence_interval

    print(
        f"95% confidence:    "
        f"[{low:.6f}, {high:.6f}]"
    )

    print()
    print("Greeks")
    print("------")

    print(f"Delta:             {delta(option):.6f}")
    print(f"Gamma:             {gamma(option):.6f}")
    print(f"Vega:              {vega(option):.6f}")
    print(f"Rho:               {rho(option):.6f}")

    print()
    print("===================================")


if __name__ == "__main__":
    main()