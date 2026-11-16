import math
from datetime import date, timedelta

from pricing_check import assess, check

SIGNAL = date(2020, 1, 25)


def bars(path, volumes=None, start=date(2019, 9, 2)):
    """Business-day bars from a list of closes."""
    out, day = [], start
    for i, close in enumerate(path):
        while day.weekday() >= 5:
            day += timedelta(days=1)
        out.append({"date": day.isoformat(), "close": close, "volume": (volumes[i] if volumes else 1_000_000)})
        day += timedelta(days=1)
    return out


def wiggle(n, base=100.0, amp=0.01):
    return [base * (1 + amp * math.sin(i)) for i in range(n)]


def as_of_for(series):
    return date.fromisoformat(series[-1]["date"])


def test_flat_stock_is_early():
    stock = bars(wiggle(110))
    bench = bars(wiggle(110, 50))
    result = assess(stock, bench, as_of_for(stock) - timedelta(days=3), as_of_for(stock))
    assert result["verdict"] == "early"


def test_big_move_before_signal_is_caught_by_trailing_window():
    # The stock jumps 60% over the last 8 sessions, before our signal date (the last day).
    path = wiggle(100) + [100 * (1.06 ** k) for k in range(1, 9)]
    stock = bars(path, volumes=[1_000_000] * 100 + [5_000_000] * 8)
    bench = bars(wiggle(108, 50))
    as_of = as_of_for(stock)
    result = assess(stock, bench, as_of, as_of)
    assert abs(result["excessSinceSignal"]) < 0.1  # only the last session falls after the signal
    assert result["judgedOn"] == "last 10 sessions"
    assert result["verdict"] == "heavily priced"
    assert result["volumeRatio"] > 4


def test_moderate_move_is_partly_priced():
    path = wiggle(100) + [100 * (1.004 ** k) for k in range(1, 9)]
    stock = bars(path, volumes=[1_000_000] * 100 + [1_800_000] * 8)
    bench = bars(wiggle(108, 50))
    as_of = as_of_for(stock)
    assert assess(stock, bench, as_of, as_of)["verdict"] == "partly priced"


def test_uses_only_bars_up_to_as_of():
    path = wiggle(100) + [300.0] * 5  # the spike happens after as-of
    stock = bars(path)
    bench = bars(wiggle(105, 50))
    as_of = date.fromisoformat(stock[99]["date"])
    assert assess(stock, bench, as_of - timedelta(days=2), as_of)["verdict"] == "early"


def test_short_history_and_fetch_errors_report_no_data():
    def fetch(ticker, start, end):
        if ticker == "BAD":
            raise OSError("delisted")
        return bars(wiggle(10)) if ticker == "NEW" else bars(wiggle(110, 50))
    result = check(["NEW", "BAD"], SIGNAL, date(2020, 1, 26), fetch=fetch)
    assert result["companies"]["NEW"]["verdict"] == "no data"
    assert result["companies"]["BAD"]["verdict"] == "no data"
