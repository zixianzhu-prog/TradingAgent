"""Isolated Kronos batch runner. Called by ai_fund_lab.forecast."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

from model import Kronos, KronosPredictor, KronosTokenizer


def main(input_name: str, output_name: str) -> None:
    payload = json.loads(Path(input_name).read_text(encoding="utf-8"))
    tickers = list(payload["series"])
    frames = []
    history_timestamps = []
    future_timestamps = []
    days = int(payload["forecast_days"])
    for ticker in tickers:
        frame = pd.DataFrame(payload["series"][ticker])
        index = pd.DatetimeIndex(pd.to_datetime(frame.pop("date")))
        frame.index = index
        frames.append(frame)
        history_timestamps.append(pd.Series(index))
        future_timestamps.append(
            pd.Series(pd.bdate_range(index[-1], periods=days + 1)[1:])
        )

    tokenizer = KronosTokenizer.from_pretrained(payload["tokenizer"])
    model = Kronos.from_pretrained(payload["model"])
    predictor = KronosPredictor(model, tokenizer, device="cpu", max_context=512)
    predictions = predictor.predict_batch(
        df_list=frames,
        x_timestamp_list=history_timestamps,
        y_timestamp_list=future_timestamps,
        pred_len=days,
        T=1.0,
        top_p=0.9,
        sample_count=int(payload["sample_count"]),
        verbose=False,
    )
    result = {}
    for ticker, frame, prediction in zip(tickers, frames, predictions):
        last_close = float(frame["close"].iloc[-1])
        predicted_close = float(prediction["close"].iloc[-1])
        result[ticker] = {
            "last_close": last_close,
            "predicted_close": predicted_close,
            "forecast_return": predicted_close / last_close - 1.0,
        }
    Path(output_name).write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

