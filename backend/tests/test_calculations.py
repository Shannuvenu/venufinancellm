import pytest

from app.services.calculations import calculate


def test_cagr_known_example():
    assert calculate("cagr", {"start": 100, "end": 121, "years": 2})["result"] == pytest.approx(10)


def test_emi_zero_interest():
    assert calculate("emi", {"principal": 1200, "rate": 0, "months": 12})["result"] == pytest.approx(100)


def test_sip_zero_interest():
    assert calculate("sip", {"payment": 100, "rate": 0, "years": 1})["result"] == pytest.approx(1200)


def test_dividend_yield():
    assert calculate("dividend_yield", {"annual_dividend": 5, "price": 100})["result"] == pytest.approx(5)


def test_options_call_payoff():
    assert calculate("options_payoff", {"spot": 120, "strike": 100, "premium": 8, "quantity": 2, "option_type": "call"})["result"] == pytest.approx(24)


def test_cagr_rejects_invalid_period():
    with pytest.raises(ValueError):
        calculate("cagr", {"start": 100, "end": 120, "years": 0})


def test_npv_uses_period_zero_cash_flow():
    result = calculate("npv", {"cashflows": [-100, 60, 60], "rate": 10})
    assert result["result"] == pytest.approx(4.1322314)


def test_irr_known_example():
    result = calculate("irr", {"cashflows": [-100, 60, 60]})
    assert result["result"] == pytest.approx(13.0662386, abs=1e-4)


def test_max_drawdown():
    result = calculate("max_drawdown", {"values": [100, 120, 90, 110]})
    assert result["result"] == pytest.approx(-25)


def test_fx_conversion_requires_positive_explicit_rate():
    result = calculate("currency_conversion", {"amount": 100, "rate": 83, "from_currency": "USD", "to_currency": "INR"})
    assert result["result"] == pytest.approx(8300)


def test_roe_rejects_undefined_denominator():
    with pytest.raises(ValueError):
        calculate("roe", {"net_income": 12, "average_equity": 0})
