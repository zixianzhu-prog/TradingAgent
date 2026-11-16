from market_profile_agent import calculate_profile, extract_market_cap


def test_liquidity_passes_above_two_million_dollars():
    row = calculate_profile([10, 11, 12], [300_000, 300_000, 300_000], 1_000_000_000)
    assert row["liquidityStatus"] == "pass"
    assert row["marketCapM"] == 1000.0
    assert row["averageDollarVolume60d"] == 3_300_000


def test_thin_liquidity_fails_and_missing_is_unknown():
    assert calculate_profile([1, 1], [100_000, 100_000])["liquidityStatus"] == "fail"
    assert calculate_profile([], [])["liquidityStatus"] == "unknown"


def test_market_cap_accepts_current_and_legacy_yfinance_keys():
    assert extract_market_cap({"marketCap": 123}) == 123
    assert extract_market_cap({"market_cap": 456}) == 456
