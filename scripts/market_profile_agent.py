from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, stdev


def calculate_profile(closes: list[float], volumes: list[float], market_cap: float | None = None) -> dict:
    pairs = [(float(c), float(v)) for c, v in zip(closes, volumes) if c and v is not None]
    dollar_volumes = [close * volume for close, volume in pairs[-60:]]
    returns = [pairs[i][0] / pairs[i - 1][0] - 1 for i in range(1, len(pairs)) if pairs[i - 1][0] > 0]
    average_dollar_volume = mean(dollar_volumes) if dollar_volumes else None
    if average_dollar_volume is None:
        liquidity = "unknown"
    elif average_dollar_volume >= 2_000_000:
        liquidity = "pass"
    elif average_dollar_volume >= 500_000:
        liquidity = "partial"
    else:
        liquidity = "fail"
    return {
        "lastPrice": pairs[-1][0] if pairs else None,
        "marketCapM": round(float(market_cap) / 1_000_000, 1) if market_cap else None,
        "averageDollarVolume60d": round(average_dollar_volume, 2) if average_dollar_volume is not None else None,
        "medianDollarVolume60d": round(median(dollar_volumes), 2) if dollar_volumes else None,
        "annualizedVolatility": round(stdev(returns) * math.sqrt(252), 6) if len(returns) > 1 else None,
        "observations": len(pairs),
        "liquidityStatus": liquidity,
    }


def extract_market_cap(fast_info) -> float | None:
    return fast_info.get("market_cap") or fast_info.get("marketCap")


def fetch_profiles(tickers: list[str], financial_caps: dict[str, float], previous: dict) -> tuple[list[dict], list[dict]]:
    import yfinance as yf

    profiles, errors = [], []
    previous_rows = {row["ticker"]: row for row in previous.get("companies", [])}
    frame = None
    try:
        frame = yf.download(tickers, period="3mo", auto_adjust=True, progress=False, group_by="ticker", threads=True)
    except Exception as exc:
        errors.append({"ticker": "ALL", "stage": "history", "error": str(exc)})
    for ticker in tickers:
        try:
            if frame is None or frame.empty:
                raise ValueError("No market history returned")
            if len(tickers) == 1:
                section = frame
            else:
                section = frame[ticker]
            closes = [float(value) for value in section["Close"].dropna().tolist()]
            volumes = [float(value) for value in section.loc[section["Close"].notna(), "Volume"].fillna(0).tolist()]
            market_cap = financial_caps.get(ticker)
            if market_cap is None:
                try:
                    fast_info = yf.Ticker(ticker).fast_info
                    market_cap = extract_market_cap(fast_info)
                except Exception as exc:
                    errors.append({"ticker": ticker, "stage": "market-cap", "error": str(exc)})
            profiles.append({"ticker": ticker, **calculate_profile(closes, volumes, market_cap), "dataStatus": "current"})
        except Exception as exc:
            cached = previous_rows.get(ticker)
            if cached:
                profiles.append({**cached, "dataStatus": "cached"})
            else:
                profiles.append({"ticker": ticker, **calculate_profile([], [], financial_caps.get(ticker)), "dataStatus": "unavailable"})
            errors.append({"ticker": ticker, "stage": "profile", "error": str(exc)})
    return profiles, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Build point-in-time market-cap, liquidity and volatility profiles")
    parser.add_argument("--theme-links", required=True)
    parser.add_argument("--financials", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    links = json.loads(Path(args.theme_links).read_text(encoding="utf-8"))
    financials = json.loads(Path(args.financials).read_text(encoding="utf-8"))
    state_path, report_path = Path(args.state), Path(args.report)
    previous = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    tickers = sorted({row["ticker"] for row in links.get("companies", [])})
    financial_caps = {row["ticker"]: float(row["market_cap_m"]) * 1_000_000 for row in financials.get("companies", []) if row.get("market_cap_m") is not None}
    profiles, errors = fetch_profiles(tickers, financial_caps, previous)
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": "60-session adjusted-close dollar volume and volatility; market cap uses filing-derived financial scenarios when available, otherwise public market metadata.",
        "companies": profiles,
        "errors": errors,
        "summary": {
            "companies": len(profiles),
            "withMarketCap": sum(row.get("marketCapM") is not None for row in profiles),
            "liquid": sum(row.get("liquidityStatus") == "pass" for row in profiles),
            "cached": sum(row.get("dataStatus") == "cached" for row in profiles),
            "errors": len(errors),
        },
    }
    lines = ["# Market Profile and Liquidity Audit", "", "> Hidden Gems 的市值、平均成交额和波动核验。市场数据失败时明确显示 cached/unavailable，不会把缺失值当作通过。", "", "| 股票 | 市值 | 60日平均成交额 | 流动性 | 年化波动 | 状态 |", "|---|---:|---:|---|---:|---|"]
    for row in sorted(profiles, key=lambda item: item["ticker"]):
        cap = f"${row['marketCapM']/1000:.2f}B" if row.get("marketCapM") is not None else "—"
        volume = f"${row['averageDollarVolume60d']/1_000_000:.2f}M" if row.get("averageDollarVolume60d") is not None else "—"
        vol = f"{row['annualizedVolatility']:.1%}" if row.get("annualizedVolatility") is not None else "—"
        lines.append(f"| {row['ticker']} | {cap} | {volume} | {row['liquidityStatus']} | {vol} | {row['dataStatus']} |")
    state_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
