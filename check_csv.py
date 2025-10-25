import sys
sys.path.insert(0, '.')
import pandas as pd

print("Loading Week 7 receiving usage CSV...")
df = pd.read_csv('data/wk7_receiving_usage.csv', header=[0, 1])

print("\nColumn structure:")
print(df.columns[:10])

print("\nFirst 3 rows:")
print(df.head(3))

print("\nLooking for Jefferson:")
player_col = None
for col in df.columns:
    if 'Player' in str(col):
        player_col = col
        break

if player_col:
    print(f"\nPlayer column: {player_col}")
    jefferson = df[df[player_col].str.contains('Jefferson', na=False, case=False)]
    if not jefferson.empty:
        print("\nJefferson row:")
        print(jefferson.iloc[0])
