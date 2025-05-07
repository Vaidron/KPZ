import pandas as pd
from binance.client import Client
from datetime import datetime, timedelta


def fetch_market_data(symbol: str, interval: str, days: int = 30) -> pd.DataFrame:
    client = Client()
    now = datetime.utcnow()
    past = now - timedelta(days=days)

    klines = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        start_str=past.strftime("%Y-%m-%d %H:%M:%S"),
        end_str=now.strftime("%Y-%m-%d %H:%M:%S")
    )

    frame = pd.DataFrame(klines, columns=[
        'ts', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_vol', 'trade_count',
        'taker_base_vol', 'taker_quote_vol', 'ignore'
    ])

    frame = frame[['ts', 'open', 'high', 'low', 'close', 'volume']]
    frame['ts'] = pd.to_datetime(frame['ts'], unit='ms')
    frame[['open', 'high', 'low', 'close', 'volume']] = frame[['open', 'high', 'low', 'close', 'volume']].astype(float)

    return frame


def rsi(prices: pd.Series, length: int = 14) -> pd.Series:
    change = prices.diff()
    up = change.clip(lower=0).rolling(length).mean()
    down = -change.clip(upper=0).rolling(length).mean()
    relative_strength = up / down
    return 100 - (100 / (1 + relative_strength))


def simple_moving_avg(prices: pd.Series, window: int) -> pd.Series:
    return prices.rolling(window=window).mean()


def bollinger(data: pd.Series, window: int = 20) -> pd.DataFrame:
    mid = simple_moving_avg(data, window)
    dev = data.rolling(window).std()
    upper = mid + (2 * dev)
    lower = mid - (2 * dev)
    return pd.DataFrame({'bb_low': lower, 'bb_mid': mid, 'bb_high': upper})


def average_true_range(df: pd.DataFrame, window: int = 14) -> pd.Series:
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - df['close'].shift()).abs()
    tr3 = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window).mean()


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['RSI_14'] = rsi(df['close'])
    df['MA_50'] = simple_moving_avg(df['close'], 50)
    df['MA_200'] = simple_moving_avg(df['close'], 200)
    bb = bollinger(df['close'])
    df = pd.concat([df, bb], axis=1)
    df['ATR_14'] = average_true_range(df)
    return df


def save_csv(df: pd.DataFrame, file_path: str):
    df.to_csv(file_path, index=False)
    print(f"Файл успешно сохранен как: {file_path}")


def main():
    symbol = "BTCUSDT"
    interval = Client.KLINE_INTERVAL_1HOUR

    data = fetch_market_data(symbol, interval)
    data = add_indicators(data)
    save_csv(data, "market_insights.csv")
    print(data.tail())


if __name__ == "__main__":
    main()
