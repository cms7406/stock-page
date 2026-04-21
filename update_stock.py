import json
from datetime import datetime, timezone, timedelta

import requests
import yfinance as yf

STOCK_SYMBOL = "301536.SZ"
SHARES = 25000
TAX_RATE = 0.10


def get_stock_price():
    ticker = yf.Ticker(STOCK_SYMBOL)

    fast_info = getattr(ticker, "fast_info", None)
    if fast_info:
        price = fast_info.get("lastPrice")
        if price:
            return float(price)

    hist = ticker.history(period="5d")
    if hist.empty:
        raise RuntimeError("No stock price data found.")

    price = hist["Close"].dropna().iloc[-1]
    return float(price)


def get_cny_to_twd_rate():
    url = "https://open.er-api.com/v6/latest/CNY"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    rate = data.get("rates", {}).get("TWD")
    if not rate:
        raise RuntimeError("TWD exchange rate not found.")

    return float(rate)


def main():
    stock_price_cny = get_stock_price()
    cny_to_twd_rate = get_cny_to_twd_rate()

    total_value_cny = stock_price_cny * SHARES
    total_value_twd = total_value_cny * cny_to_twd_rate
    net_value_twd_after_tax = total_value_twd * (1 - TAX_RATE)

    tw_timezone = timezone(timedelta(hours=8))
    updated_at = datetime.now(tw_timezone).strftime("%Y-%m-%d %H:%M:%S")

    output = {
        "stock_symbol": STOCK_SYMBOL,
        "shares": SHARES,
        "tax_rate": TAX_RATE,
        "stock_price_cny": round(stock_price_cny, 4),
        "total_value_cny": round(total_value_cny, 2),
        "cny_to_twd_rate": round(cny_to_twd_rate, 6),
        "total_value_twd": round(total_value_twd, 2),
        "net_value_twd_after_tax": round(net_value_twd_after_tax, 2),
        "updated_at": updated_at
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("data.json updated successfully")


if __name__ == "__main__":
    main()
