import requests
from datetime import datetime, timezone

API = "https://api.dexscreener.com"
MIN_LIQUIDITY_USD = 10_000
MIN_VOLUME_5M_USD = 5_000
MIN_BUYS_5M = 10

def get_json(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()

def scan():
    profiles = get_json(f"{API}/token-profiles/latest/v1")
    seen = set()

    for profile in profiles:
        if profile.get("chainId") != "solana":
            continue

        address = profile.get("tokenAddress")
        if not address or address in seen:
            continue
        seen.add(address)

        try:
            pairs = get_json(
                f"{API}/token-pairs/v1/solana/{address}"
            )
        except requests.RequestException:
            continue

        for pair in pairs:
            liquidity = (pair.get("liquidity") or {}).get("usd") or 0
            volume = (pair.get("volume") or {}).get("m5") or 0
            txns = (pair.get("txns") or {}).get("m5") or {}
            buys = txns.get("buys") or 0
            sells = txns.get("sells") or 0

            if (
                liquidity >= MIN_LIQUIDITY_USD
                and volume >= MIN_VOLUME_5M_USD
                and buys >= MIN_BUYS_5M
            ):
                print({
                    "time": datetime.now(timezone.utc).isoformat(),
                    "name": (pair.get("baseToken") or {}).get("name"),
                    "symbol": (pair.get("baseToken") or {}).get("symbol"),
                    "liquidity_usd": liquidity,
                    "volume_5m_usd": volume,
                    "buys_5m": buys,
                    "sells_5m": sells,
                    "address": address,
                    "url": pair.get("url"),
                })

if __name__ == "__main__":
    scan()
