import logging

import ta
import yfinance as yf

from app.application.interfaces.indicator_service import IIndicatorService
from app.domain.entities.stock import IndicatorResult

logger = logging.getLogger(__name__)

VALID_TYPES = {"macd", "rsi", "sma", "ema", "bb"}


class TALibIndicatorService(IIndicatorService):
    async def calculate(
        self,
        ticker: str,
        indicator_type: str,
        interval: str,
        period_range: str,
        period: int = 14,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> IndicatorResult:
        try:
            hist = yf.Ticker(ticker).history(period=period_range, interval=interval)
        except Exception as e:
            logger.error("indicator fetch failed for %s: %s", ticker, e)
            return IndicatorResult(ticker=ticker, type=indicator_type)

        if hist.empty:
            return IndicatorResult(ticker=ticker, type=indicator_type)

        close = hist["Close"].dropna()
        timestamps = [int(ts.timestamp() * 1000) for ts in close.index]

        try:
            if indicator_type == "rsi":
                values = ta.momentum.RSIIndicator(close=close, window=period).rsi()
                data = [{"t": t, "v": _sf(v)} for t, v in zip(timestamps, values.tolist())]

            elif indicator_type == "macd":
                ind = ta.trend.MACD(
                    close=close, window_slow=slow, window_fast=fast, window_sign=signal
                )
                data = [
                    {
                        "t": t,
                        "macd": _sf(ind.macd().tolist()[i]),
                        "signal": _sf(ind.macd_signal().tolist()[i]),
                        "histogram": _sf(ind.macd_diff().tolist()[i]),
                    }
                    for i, t in enumerate(timestamps)
                ]

            elif indicator_type == "sma":
                values = ta.trend.SMAIndicator(close=close, window=period).sma_indicator()
                data = [{"t": t, "v": _sf(v)} for t, v in zip(timestamps, values.tolist())]

            elif indicator_type == "ema":
                values = ta.trend.EMAIndicator(close=close, window=period).ema_indicator()
                data = [{"t": t, "v": _sf(v)} for t, v in zip(timestamps, values.tolist())]

            elif indicator_type == "bb":
                bb = ta.volatility.BollingerBands(close=close, window=period, window_dev=2)
                upper = bb.bollinger_hband().tolist()
                middle = bb.bollinger_mavg().tolist()
                lower = bb.bollinger_lband().tolist()
                data = [
                    {
                        "t": t,
                        "upper": _sf(upper[i]),
                        "middle": _sf(middle[i]),
                        "lower": _sf(lower[i]),
                    }
                    for i, t in enumerate(timestamps)
                ]

            else:
                data = []

        except Exception as e:
            logger.error("indicator calc failed for %s %s: %s", ticker, indicator_type, e)
            data = []

        return IndicatorResult(ticker=ticker, type=indicator_type, data=data)


def _sf(v) -> float | None:  # type: ignore[return]
    try:
        f = float(v)
        return None if (f != f) else f
    except (TypeError, ValueError):
        return None
