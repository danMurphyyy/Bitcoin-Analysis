import warnings
warnings.filterwarnings("ignore")

from openbb import openbb
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from scipy.signal import find_peaks

#configure pandas display
pd.set_option('display.max_columns', None)
pd.set_option('display.precision', 4)

#fetch crypto data
def fetch_crypto_data(symbol) -> pd.DataFrame:
    crypto_data = openbb.crypto.historical(symbol, provider='yfinance', start_date=datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d").to_df()
    return crypto_data

btc = fetch_crypto_data('BTC-USD')

#Calculate technical indicators
def calculate_technical_indicators(df) -> pd.DataFrame:
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    return df

btc = calculate_technical_indicators(btc)

#Bollinger Bands
def calculate_bollinger_bands(df) -> pd.DataFrame:
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (2 * df['BB_Std'])
    df['BB_Lower'] = df['BB_Middle'] - (2 * df['BB_Std'])
    df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
    return df

btc = calculate_bollinger_bands(btc)

#RSI
def calculate_rsi(df, period=14) -> pd.DataFrame:
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

btc = calculate_rsi(btc)

#MACD
def calculate_macd(df) -> pd.DataFrame:
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    return df

btc = calculate_macd(btc)

#ATR (average true range)
def calculate_atr(df, period=14) -> pd.DataFrame:
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=period).mean()
    return df

btc = calculate_atr(btc)

#identify support and resistance levels
def identify_support_resistance(df) -> pd.DataFrame:
    peaks_high, _ = find_peaks(df['High'], distance=20, prominence=df['High'].std())
    peaks_low, _ = find_peaks(-df['Low'], distance=20, prominence=df['Low'].std())

    resistance_levels = df['High'].iloc[peaks_high].nlargest(3).values
    support_levels = df['Low'].iloc[peaks_low].nsmallest(3).values
    return df, resistance_levels, support_levels

btc, btc_resistance_levels, btc_support_levels = identify_support_resistance(btc)

def print_values(df, resistance_levels, support_levels):
    print("Latest BTC Price:", df['Close'].iloc[-1])
    print("20-day SMA:", df['SMA_20'].iloc[-1])
    print("50-day SMA:", df['SMA_50'].iloc[-1])
    print("200-day SMA:", df['SMA_200'].iloc[-1])
    print("Bollinger Band Width:", df['BB_Width'].iloc[-1])
    print(f"RSI: {df['RSI'].iloc[-1]:.2f} {'(Overbought)' if df['RSI'].iloc[-1] > 70 else '(Oversold)' if df['RSI'].iloc[-1] < 30 else ''}")
    print(f"MACD: {df['MACD'].iloc[-1]:.2f} {'(Bullish)' if df['MACD'].iloc[-1] > df['MACD_Signal'].iloc[-1] else '(Bearish)'}")
    print(f"ATR: {df['ATR'].iloc[-1]:.2f}")
    print("Resistance Levels:", resistance_levels)
    print("Support Levels:", support_levels)

print_values(btc, btc_resistance_levels, btc_support_levels)

#create a comprehensive chart
def create_comprehensive_chart() -> go.Figure:
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.4, 0.15, 0.15, 0.15, 0.15],
        subplot_titles=("BTC Price with SMAs and Bollinger Bands", "Volume", "RSI", "MACD", "ATR")
    )
    return fig

fig = create_comprehensive_chart()

