import math


def calculate(kind: str, v: dict) -> dict:
    """Deterministic calculations. Inputs are explicit; percentages are entered as percents."""
    if kind == "cagr":
        start, end, years = float(v["start"]), float(v["end"]), float(v["years"])
        if start <= 0 or end < 0 or years <= 0:
            raise ValueError("Start value and period must be positive; ending value cannot be negative.")
        result = ((end / start) ** (1 / years) - 1) * 100
        formula = "((ending value / starting value) ^ (1 / years) - 1) × 100"
    elif kind == "compound_interest":
        principal, rate, years = float(v["principal"]), float(v["rate"]), float(v["years"])
        frequency = int(v.get("frequency", 1))
        if principal < 0 or years < 0 or frequency < 1 or rate <= -100:
            raise ValueError("Principal and years cannot be negative, rate must exceed -100%, and frequency must be at least 1.")
        result = principal * (1 + rate / 100 / frequency) ** (frequency * years)
        formula = "principal × (1 + annual rate / compounding periods) ^ periods"
    elif kind == "sip":
        payment, rate, years = float(v["payment"]), float(v["rate"]), float(v["years"])
        months = int(round(years * 12))
        if payment < 0 or months < 1 or rate <= -1200:
            raise ValueError("Payment cannot be negative, period must be at least one month, and annual rate must exceed -1200%.")
        monthly = rate / 1200
        result = payment * months if monthly == 0 else payment * (((1 + monthly) ** months - 1) / monthly) * (1 + monthly)
        formula = "monthly payment × (((1 + monthly rate) ^ months - 1) / monthly rate) × (1 + monthly rate)"
    elif kind == "emi":
        principal, annual_rate, months = float(v["principal"]), float(v["rate"]), int(v["months"])
        if principal < 0 or months < 1 or annual_rate <= -1200:
            raise ValueError("Principal cannot be negative, term must be at least one month, and annual rate must exceed -1200%.")
        monthly = annual_rate / 1200
        result = principal / months if monthly == 0 else principal * monthly * (1 + monthly) ** months / ((1 + monthly) ** months - 1)
        formula = "principal × r × (1 + r)^n / ((1 + r)^n - 1), where r is monthly rate"
    elif kind == "return":
        start, end = float(v["start"]), float(v["end"])
        if start == 0:
            raise ValueError("Starting value cannot be zero.")
        result = (end / start - 1) * 100
        formula = "((ending value / starting value) - 1) × 100"
    elif kind == "dividend_yield":
        dividend, price = float(v["annual_dividend"]), float(v["price"])
        if price <= 0:
            raise ValueError("Price must be positive.")
        result = dividend / price * 100
        formula = "annual dividend per share / price per share × 100"
    elif kind == "margin":
        numerator, revenue = float(v["profit"]), float(v["revenue"])
        if revenue == 0:
            raise ValueError("Revenue cannot be zero.")
        result = numerator / revenue * 100
        formula = "profit / revenue × 100"
    elif kind == "npv":
        cashflows, rate = list(map(float, v["cashflows"])), float(v["rate"]) / 100
        if not cashflows or rate <= -1:
            raise ValueError("Provide at least one dated cash flow and a rate greater than -100%.")
        result = sum(cf / ((1 + rate) ** period) for period, cf in enumerate(cashflows))
        formula = "sum of cash flow(t) / (1 + discount rate)^t; first item is period 0"
    elif kind == "irr":
        cashflows = list(map(float, v["cashflows"]))
        if len(cashflows) < 2 or not (any(cf < 0 for cf in cashflows) and any(cf > 0 for cf in cashflows)):
            raise ValueError("IRR needs at least two cash flows with both negative and positive values.")
        def npv_at(rate):
            if rate <= -1: return float("inf")
            return sum(cf / ((1 + rate) ** period) for period, cf in enumerate(cashflows))
        low, high = -0.9999, 1.0
        while npv_at(low) * npv_at(high) > 0 and high < 1e6:
            high = high * 2 + 1
        if npv_at(low) * npv_at(high) > 0:
            raise ValueError("Could not bracket an IRR for these cash flows.")
        for _ in range(200):
            mid = (low + high) / 2
            if abs(npv_at(mid)) < 1e-9: break
            if npv_at(low) * npv_at(mid) <= 0: high = mid
            else: low = mid
        result = mid * 100
        formula = "rate that makes NPV of periodic cash flows equal zero (numerically solved)"
    elif kind in {"present_value", "future_value"}:
        amount, rate, periods = float(v["amount"]), float(v["rate"]) / 100, float(v["periods"])
        if periods < 0 or rate <= -1:
            raise ValueError("Periods cannot be negative and rate must be greater than -100%.")
        result = amount / (1 + rate) ** periods if kind == "present_value" else amount * (1 + rate) ** periods
        formula = "future value / (1 + rate)^periods" if kind == "present_value" else "present value × (1 + rate)^periods"
    elif kind == "eps":
        earnings, shares = float(v["net_income"]), float(v["shares"])
        if shares <= 0: raise ValueError("Shares outstanding must be positive.")
        result = earnings / shares
        formula = "net income available to common shareholders / weighted-average shares"
    elif kind in {"pe", "pb", "debt_to_equity", "roe", "roic", "fcf"}:
        if kind == "pe": numerator, denominator, label = float(v["price_per_share"]), float(v["eps"]), "price per share / earnings per share"
        elif kind == "pb": numerator, denominator, label = float(v["price_per_share"]), float(v["book_value_per_share"]), "price per share / book value per share"
        elif kind == "debt_to_equity": numerator, denominator, label = float(v["total_debt"]), float(v["equity"]), "total debt / equity"
        elif kind == "roe": numerator, denominator, label = float(v["net_income"]), float(v["average_equity"]), "net income / average equity"
        elif kind == "roic": numerator, denominator, label = float(v["nopat"]), float(v["invested_capital"]), "NOPAT / invested capital"
        else:
            result = float(v["operating_cash_flow"]) - float(v["capital_expenditure"])
            formula = "operating cash flow - capital expenditure"
            numerator = denominator = None
        if kind != "fcf":
            if denominator == 0: raise ValueError("Denominator cannot be zero.")
            result = numerator / denominator
            formula = label
            if kind in {"roe", "roic"}: result *= 100; formula += " × 100"
    elif kind == "working_capital":
        result = float(v["current_assets"]) - float(v["current_liabilities"])
        formula = "current assets - current liabilities"
    elif kind == "futures_pnl":
        entry, exit_price, quantity, multiplier = map(float, (v["entry_price"], v["exit_price"], v["quantity"], v.get("multiplier", 1)))
        direction = v.get("direction", "long").lower()
        if quantity < 0 or multiplier <= 0 or direction not in {"long", "short"}:
            raise ValueError("Use non-negative quantity, positive multiplier, and long or short direction.")
        result = (exit_price - entry) * quantity * multiplier * (1 if direction == "long" else -1)
        formula = "(exit price - entry price) × quantity × multiplier × direction"
    elif kind == "currency_conversion":
        amount, rate = float(v["amount"]), float(v["rate"])
        if rate <= 0: raise ValueError("Conversion rate must be positive.")
        result = amount * rate
        formula = "amount in source currency × supplied source-to-target exchange rate"
    elif kind == "inflation_adjusted_return":
        investment_return, inflation = float(v["return_rate"]), float(v["inflation_rate"])
        if investment_return <= -100 or inflation <= -100: raise ValueError("Rates must be greater than -100%.")
        result = ((1 + investment_return / 100) / (1 + inflation / 100) - 1) * 100
        formula = "((1 + nominal return) / (1 + inflation) - 1) × 100"
    elif kind == "risk_reward":
        entry, target, stop = map(float, (v["entry"], v["target"], v["stop"]))
        direction = v.get("direction", "long").lower()
        reward = target - entry if direction == "long" else entry - target
        risk = entry - stop if direction == "long" else stop - entry
        if direction not in {"long", "short"} or risk <= 0 or reward < 0:
            raise ValueError("Check direction: stop must define positive risk and target cannot imply negative reward.")
        result = reward / risk
        formula = "potential reward / potential risk; excludes gap risk, costs and slippage"
    elif kind == "max_drawdown":
        values = list(map(float, v["values"]))
        if not values or any(x < 0 for x in values): raise ValueError("Provide a non-empty series of non-negative portfolio values.")
        peak = values[0]; result = 0.0
        for value in values:
            peak = max(peak, value)
            if peak: result = min(result, value / peak - 1)
        result *= 100
        formula = "minimum(value(t) / prior running peak - 1) × 100"
    elif kind == "volatility":
        returns = list(map(float, v["returns"]))
        periods = float(v.get("periods_per_year", 252))
        if len(returns) < 2 or periods <= 0: raise ValueError("Provide at least two periodic returns and a positive periods-per-year value.")
        mean = sum(returns) / len(returns)
        variance = sum((x - mean) ** 2 for x in returns) / (len(returns) - 1)
        result = variance ** 0.5 * periods ** 0.5
        formula = "sample standard deviation(period returns) × sqrt(periods per year); returns as decimals"
    elif kind == "sharpe":
        returns = list(map(float, v["returns"])); rf = float(v.get("risk_free_rate", 0)) / 100
        periods = float(v.get("periods_per_year", 252))
        if len(returns) < 2 or periods <= 0: raise ValueError("Provide at least two periodic returns and a positive periods-per-year value.")
        mean = sum(returns) / len(returns); std = (sum((x - mean) ** 2 for x in returns) / (len(returns) - 1)) ** 0.5
        if std == 0: raise ValueError("Sharpe ratio is undefined when return volatility is zero.")
        result = (mean - rf / periods) / std * periods ** 0.5
        formula = "mean(period return - periodic risk-free rate) / sample standard deviation × sqrt(periods per year)"
    elif kind == "sortino":
        returns = list(map(float, v["returns"])); target = float(v.get("target_return", 0)) / 100
        periods = float(v.get("periods_per_year", 252))
        if len(returns) < 2 or periods <= 0: raise ValueError("Provide at least two periodic returns and a positive periods-per-year value.")
        downside = [(min(x - target / periods, 0)) ** 2 for x in returns]
        downside_deviation = (sum(downside) / len(returns)) ** 0.5
        if downside_deviation == 0: raise ValueError("Sortino ratio is undefined when downside deviation is zero.")
        result = (sum(returns) / len(returns) - target / periods) / downside_deviation * periods ** 0.5
        formula = "mean(period return - periodic target) / downside deviation × sqrt(periods per year)"
    elif kind == "beta":
        returns, benchmark = list(map(float, v["returns"])), list(map(float, v["benchmark_returns"]))
        if len(returns) != len(benchmark) or len(returns) < 2: raise ValueError("Asset and benchmark return series must have the same length of at least two.")
        mean_a, mean_b = sum(returns) / len(returns), sum(benchmark) / len(benchmark)
        cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(returns, benchmark)) / (len(returns) - 1)
        var_b = sum((b - mean_b) ** 2 for b in benchmark) / (len(benchmark) - 1)
        if var_b == 0: raise ValueError("Beta is undefined for a benchmark with zero variance.")
        result = cov / var_b
        formula = "sample covariance(asset returns, benchmark returns) / sample variance(benchmark returns)"
    elif kind == "correlation":
        a, b = list(map(float, v["returns"])), list(map(float, v["other_returns"]))
        if len(a) != len(b) or len(a) < 2: raise ValueError("Return series must have the same length of at least two.")
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
        if den == 0: raise ValueError("Correlation is undefined when either series has zero variance.")
        result = cov / den
        formula = "Pearson correlation of paired periodic returns"
    elif kind == "options_payoff":
        spot, strike, premium, quantity = map(float, (v["spot"], v["strike"], v["premium"], v.get("quantity", 1)))
        option_type = v["option_type"].lower()
        if quantity < 0 or option_type not in {"call", "put"}:
            raise ValueError("Use a non-negative quantity and option_type call or put.")
        intrinsic = max(spot - strike, 0) if option_type == "call" else max(strike - spot, 0)
        result = (intrinsic - premium) * quantity
        formula = f"({option_type} intrinsic value at expiry - premium) × quantity; excludes costs and contract multiplier"
    else:
        raise ValueError("Unsupported calculation.")
    if not math.isfinite(result):
        raise ValueError("Calculation produced a non-finite result.")
    assumptions = ["Uses only the supplied inputs.", "Excludes taxes, fees and transaction costs unless explicitly included."]
    if kind == "sip":
        assumptions.append("Assumes each monthly contribution is made at the beginning of the month.")
    if kind == "options_payoff":
        assumptions.append("Quantity is treated as underlying units; exchange contract multipliers are not applied.")
    return {"kind": kind, "result": result, "formula": formula, "inputs": v,
            "assumptions": assumptions,
            "currency": v.get("currency", "unspecified"), "data_timestamp": None}
