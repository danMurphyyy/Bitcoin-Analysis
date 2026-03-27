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