from datetime import datetime
import pandas as pd
import os
columns = ['year', 'month', 'day', 'hour', 'minute', 'second']
filename = "2.csv"
now = datetime.now()
new_row = {
    'year': now.year,
    'month': now.month,
    'day': now.day,
    'hour': now.hour,
    'minute': now.minute,
    'second': now.second
}
if os.path.exists(filename):
    df = pd.read_csv(filename)
else:
    df = pd.DataFrame(columns=columns)
df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
df.to_csv(filename, index=False)
print(df)
