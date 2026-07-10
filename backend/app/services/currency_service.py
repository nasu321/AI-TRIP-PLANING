"""
Currency Service — exchange rate lookup with mock fallback.
"""
import httpx
import logging
from typing import Dict
from app.config import settings

logger = logging.getLogger(__name__)

# Approximate exchange rates relative to USD (mock)
MOCK_RATES_TO_USD = {
    "USD": 1.0, "EUR": 1.09, "GBP": 1.27, "JPY": 0.0067,
    "AUD": 0.65, "CAD": 0.74, "CHF": 1.13, "SGD": 0.74,
    "AED": 0.27, "THB": 0.028, "IDR": 0.000063, "INR": 0.012,
    "MXN": 0.057, "BRL": 0.19, "KRW": 0.00073, "CNY": 0.138,
    "TRY": 0.031, "ZAR": 0.053, "SAR": 0.27, "QAR": 0.27,
}


async def convert_currency(amount: float, from_currency: str, to_currency: str = "USD") -> float:
    """Convert amount from one currency to another."""
    if not settings.USE_MOCK_CURRENCY and settings.CURRENCY_API_KEY:
        return await _real_convert(amount, from_currency, to_currency)
    return _mock_convert(amount, from_currency, to_currency)


async def _real_convert(amount: float, from_curr: str, to_curr: str) -> float:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://v6.exchangerate-api.com/v6/{settings.CURRENCY_API_KEY}/pair/{from_curr}/{to_curr}/{amount}",
                timeout=10,
            )
            data = resp.json()
            return data.get("conversion_result", amount)
    except Exception as e:
        logger.warning(f"Currency API failed: {e}")
        return _mock_convert(amount, from_curr, to_curr)


def _mock_convert(amount: float, from_curr: str, to_curr: str) -> float:
    from_rate = MOCK_RATES_TO_USD.get(from_curr.upper(), 1.0)
    to_rate = MOCK_RATES_TO_USD.get(to_curr.upper(), 1.0)
    usd = amount * from_rate
    return round(usd / to_rate, 2)


def get_supported_currencies() -> Dict[str, float]:
    return MOCK_RATES_TO_USD
