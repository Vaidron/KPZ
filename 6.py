import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
num_points = 50
timestamps = pd.date_range(end=pd.Timestamp.now(), periods=num_points, freq='D')
rsi_data = np.random.uniform(20, 80, num_points)
rsi_df = pd.DataFrame({
    'timestamp': timestamps,
    'rsi_value': rsi_data
})
csv_path = "rsi_indicators_log.csv"
rsi_df.to_csv(csv_path, index=False)
rsi_df = pd.read_csv(csv_path, parse_dates=['timestamp'])
fig = plt.figure(figsize=(14, 4))
titles = ['RSI as Bars', 'RSI as Dots', 'RSI as Line']
plot_types = ['bar', 'scatter', 'line']
colors = ['#87CEEB', '#FF8C00', '#228B22']
for i, (plot_type, title, color) in enumerate(zip(plot_types, titles, colors), 1):
    ax = fig.add_subplot(1, 3, i)
    if plot_type == 'bar':
        ax.bar(rsi_df['timestamp'], rsi_df['rsi_value'], color=color)
    elif plot_type == 'scatter':
        ax.scatter(rsi_df['timestamp'], rsi_df['rsi_value'], color=color, s=15)
    elif plot_type == 'line':
        ax.plot(rsi_df['timestamp'], rsi_df['rsi_value'], color=color)
    
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=40)
fig.tight_layout()
plt.savefig("rsi_chart_variants.png")
plt.show()
