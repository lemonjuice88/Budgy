import httpx
from fastapi import HTTPException, status

FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"


async def convert_amount(amount: float, from_currency: str, to_currency: str) -> float:
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return round(amount, 2)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                FRANKFURTER_URL,
                params={"amount": amount, "from": from_currency, "to": to_currency},
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            f"Güncel kur bilgisi alınamadı ({from_currency} -> {to_currency})",
        ) from exc

    rates = response.json().get("rates", {})
    if to_currency not in rates:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            f"{to_currency} için kur bilgisi bulunamadı",
        )
    return round(rates[to_currency], 2)
