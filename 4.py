import pandas as pd
from binance.client import Client
from datetime import datetime, timedelta
def compute_rsi(prices: pd.Series, length: int) -> pd.Series:
    diff = prices.diff()
    up = diff.clip(lower=0)
    down = -diff.clip(upper=0)
    roll_up = up.rolling(window=length).mean()
    roll_down = down.rolling(window=length).mean()
    rs = roll_up / roll_down
    return 100 - (100 / (1 + rs))
def load_ohlcv_data(pair: str = "BTCUSDT", interval=Client.KLINE_INTERVAL_1MINUTE, days_back: int = 1) -> pd.DataFrame:
    client = Client()
    now = datetime.utcnow().replace(second=0, microsecond=0)
    since = now - timedelta(days=days_back)
    candles = client.get_historical_klines(
        symbol=pair,
        interval=interval,
        start_str=since.strftime("%Y-%m-%d %H:%M:%S"),
        end_str=now.strftime("%Y-%m-%d %H:%M:%S")
    )
    ohlcv = pd.DataFrame(candles, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
    ])
    ohlcv = ohlcv[['timestamp', 'open', 'close']]
    ohlcv['timestamp'] = pd.to_datetime(ohlcv['timestamp'], unit='ms')
    ohlcv[['open', 'close']] = ohlcv[['open', 'close']].astype(float)
    return ohlcv
def run_analysis():
    df = load_ohlcv_data()
    rsi_periods = [14, 27, 100]
    for length in rsi_periods:
        df[f'RSI_{length}'] = compute_rsi(df['close'], length)
    print(df.tail())
if __name__ == "__main__":
    run_analysis()
