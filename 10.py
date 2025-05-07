import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta
from datetime import datetime, timedelta

np.random.seed(42)
num_points = 300
base_price = 100
price_changes = np.random.normal(0, 2, num_points)
close_prices = base_price + np.cumsum(price_changes)

data = pd.DataFrame({
    "time": [datetime.now() - timedelta(minutes=5 * i) for i in range(num_points)][::-1],
    "close": close_prices,
    "high": close_prices + np.random.uniform(0.5, 1.5, num_points),
    "low": close_prices - np.random.uniform(0.5, 1.5, num_points)
})

class Trade:
    def __init__(self, entry_price, sl, tp, entry_time):
        self.entry_price = entry_price
        self.sl = sl
        self.tp = tp
        self.entry_time = entry_time
        self.exit_time = None
        self.exit_price = None
        self.result = None


class Backtester:
    def __init__(self, data: pd.DataFrame, initial_balance=1000, tp_ratio=2, sl_ratio=1):
        self.data = data.copy()
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.tp_ratio = tp_ratio
        self.sl_ratio = sl_ratio
        self.trades = []
        self.history = []

    def run(self):
        print("Запуск бектестера...")
        self.data["rsi"] = ta.momentum.RSIIndicator(self.data["close"], window=14).rsi()

        in_position = False
        current_trade = None

        for index in range(100, len(self.data)):
            candle = self.data.iloc[index]
            price = candle["close"]
            rsi = candle["rsi"]

            if in_position and current_trade:
                low = candle["low"]
                high = candle["high"]

                if low <= current_trade.sl:
                    current_trade.exit_price = current_trade.sl
                    current_trade.exit_time = candle["time"]
                    current_trade.result = "SL"
                    self.trades.append(current_trade)
                    self.balance -= (current_trade.entry_price - current_trade.sl)
                    in_position = False
                elif high >= current_trade.tp:
                    current_trade.exit_price = current_trade.tp
                    current_trade.exit_time = candle["time"]
                    current_trade.result = "TP"
                    self.trades.append(current_trade)
                    self.balance += (current_trade.tp - current_trade.entry_price)
                    in_position = False

            if not in_position and rsi < 40:
                sl = price - self.sl_ratio
                tp = price + self.tp_ratio
                current_trade = Trade(price, sl, tp, candle["time"])
                in_position = True

            self.history.append((candle["time"], self.balance))

        self.print_stats()
        self.plot_balance()

    def print_stats(self):
        wins = sum(1 for t in self.trades if t.result == "TP")
        losses = sum(1 for t in self.trades if t.result == "SL")
        total = len(self.trades)

        win_rate = wins / total * 100 if total else 0
        profit = self.balance - self.initial_balance

        print("\n Статистика бектесту:")
        print(f"Загальна кількість угод: {total}")
        print(f"Виграних: {wins} | Програних: {losses}")
        print(f"Win rate: {win_rate:.2f}%")
        print(f"Зміна балансу: {profit:.2f} USDT")

    def plot_balance(self):
        times, balances = zip(*self.history)
        plt.figure(figsize=(10, 5))
        plt.plot(times, balances)
        plt.title("Баланс під час бектесту")
        plt.xlabel("Час")
        plt.ylabel("Баланс")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

bt = Backtester(data)
bt.run()
