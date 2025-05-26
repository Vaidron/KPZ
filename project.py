import pandas as pd
import numpy as np

np.random.seed(42)
n = 500
close = np.cumsum(np.random.randn(n)) + 100
high = close + np.random.rand(n) * 2
low = close - np.random.rand(n) * 2
open_ = close + np.random.randn(n)
volume = np.random.randint(100, 1000, size=n)

df = pd.DataFrame({
    'Open': open_,
    'High': high,
    'Low': low,
    'Close': close,
    'Volume': volume
})

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

df['EMA50'] = ema(df['Close'], 50)

def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['RSI'] = rsi(df['Close'])

def macd(series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    return macd_line, signal_line

df['MACD'], df['MACD_signal'] = macd(df['Close'])

df['long_entry'] = (
    (df['RSI'].shift(1) < 30) & (df['RSI'] >= 30) &
    (df['MACD'].shift(1) < df['MACD_signal'].shift(1)) & (df['MACD'] > df['MACD_signal']) &
    (df['Close'] > df['EMA50'])
)

df['short_entry'] = (
    (df['RSI'].shift(1) > 70) & (df['RSI'] <= 70) &
    (df['MACD'].shift(1) > df['MACD_signal'].shift(1)) & (df['MACD'] < df['MACD_signal']) &
    (df['Close'] < df['EMA50'])
)

trades = []
in_trade = False
side = None
entry_price = 0
TP = 0.05
SL = 0.02

for i in range(1, len(df)):
    price = df.loc[i, 'Close']
    if not in_trade:
        if df.loc[i, 'long_entry']:
            in_trade = True
            side = 'long'
            entry_price = price
        elif df.loc[i, 'short_entry']:
            in_trade = True
            side = 'short'
            entry_price = price
    else:
        if side == 'long':
            if price >= entry_price * (1 + TP):
                trades.append({'entry': entry_price, 'exit': price, 'profit': TP, 'side': 'long'})
                in_trade = False
            elif price <= entry_price * (1 - SL):
                trades.append({'entry': entry_price, 'exit': price, 'profit': -SL, 'side': 'long'})
                in_trade = False
        elif side == 'short':
            if price <= entry_price * (1 - TP):
                trades.append({'entry': entry_price, 'exit': price, 'profit': TP, 'side': 'short'})
                in_trade = False
            elif price >= entry_price * (1 + SL):
                trades.append({'entry': entry_price, 'exit': price, 'profit': -SL, 'side': 'short'})
                in_trade = False

results = pd.DataFrame(trades)
total_return = results['profit'].sum()
win_rate = (results['profit'] > 0).mean()

print(f"Загальний прибуток: {total_return:.2%}")
print(f"Відсоток виграшних трейдів: {win_rate:.2%}")
