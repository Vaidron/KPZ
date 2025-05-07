import pandas as pd
import numpy as np
from binance.client import Client
from dataclasses import dataclass
from datetime import datetime
import time

@dataclass
class Signal:
    time: datetime
    asset: str
    qty: float
    direction: str
    entry: float
    take_profit: float
    stop_loss: float
    status: str = "Open"

class SolTrader:
    def __init__(self, qty: float = 1.0):
        self.symbol = "SOLUSDT"
        self.qty = qty
        self.client = Client()

    def get_price_data(self, limit: int = 100) -> pd.DataFrame:
        candles = self.client.get_klines(symbol=self.symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
        structured = [
            [
                datetime.utcfromtimestamp(item[0] / 1000),
                float(item[1]), float(item[2]),
                float(item[3]), float(item[4])
            ] for item in candles
        ]
        return pd.DataFrame(structured, columns=['time', 'open', 'high', 'low', 'close'])

    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df['EMA14'] = df['close'].ewm(span=14, adjust=False).mean()

        change = df['close'].diff()
        gain = change.clip(lower=0).rolling(window=14).mean()
        loss = -change.clip(upper=0).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        hl = df['high'] - df['low']
        hc = abs(df['high'] - df['close'].shift())
        lc = abs(df['low'] - df['close'].shift())
        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=14).mean()

        plus_dm = np.where((df['high'] - df['high'].shift()) > (df['low'].shift() - df['low']),
                           df['high'] - df['high'].shift(), 0)
        minus_dm = np.where((df['low'].shift() - df['low']) > (df['high'] - df['high'].shift()),
                            df['low'].shift() - df['low'], 0)

        df['+DI'] = 100 * (pd.Series(plus_dm).rolling(14).mean() / df['ATR'])
        df['-DI'] = 100 * (pd.Series(minus_dm).rolling(14).mean() / df['ATR'])
        df['ADX'] = abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI']) * 100

        return df

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        df = self.add_indicators(df)
        latest = df.iloc[-1]

        price = latest['close']
        ema = latest['EMA14']
        rsi = latest['RSI']
        adx = latest['ADX']

        if pd.isna(rsi) or pd.isna(adx):
            return None

        side = None
        if rsi < 30 and price < ema:
            side = "BUY"
        elif rsi > 70 and price > ema:
            side = "SELL"

        if side and adx > 35:
            tp = round(price * 1.05 if side == "BUY" else price * 0.95, 2)
            sl = round(price * 0.98 if side == "BUY" else price * 1.02, 2)
            return Signal(datetime.now(), self.symbol, self.qty, side, price, tp, sl)
        return None

def run_sol_bot(trader: SolTrader):
    while True:
        try:
            df = trader.get_price_data()
            signal = trader.analyze(df)
            if signal:
                print(f"[{signal.time}] SIGNAL: {signal.direction} {signal.asset} @ {signal.entry}")
                print(f"   → Take Profit: {signal.take_profit}, Stop Loss: {signal.stop_loss}")
            else:
                print(f"[{datetime.now()}] No signal for SOLUSDT.")
            time.sleep(7)
        except Exception as e:
            print(f"[{datetime.now()}] Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    sol_bot = SolTrader(qty=1.0)
    run_sol_bot(sol_bot)
