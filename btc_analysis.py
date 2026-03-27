import warnings
warnings.filterwarnings("ignore")

from openbb import obb
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from scipy.signal import find_peaks

#configure pandas display
pd.set_option('display.max_columns', None)
pd.set_option('display.precision', 4)

#fetch crypto data
def fetch_crypto_data(symbol) -> pd.DataFrame:
    start_date = (datetime.now() - timedelta(days=365)).date().isoformat()
    crypto_data = obb.crypto.price.historical(
        symbol,
        provider='yfinance',
        start_date=start_date
    ).to_df()
    crypto_data = crypto_data.rename(
        columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume',
        }
    )
    return crypto_data

#Calculate technical indicators
def calculate_technical_indicators(df) -> pd.DataFrame:
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    return df

#Bollinger Bands
def calculate_bollinger_bands(df) -> pd.DataFrame:
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (2 * df['BB_Std'])
    df['BB_Lower'] = df['BB_Middle'] - (2 * df['BB_Std'])
    df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
    return df

#RSI
def calculate_rsi(df, period=14) -> pd.DataFrame:
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

#MACD
def calculate_macd(df) -> pd.DataFrame:
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    return df

#ATR (average true range)
def calculate_atr(df, period=14) -> pd.DataFrame:
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=period).mean()
    return df

#identify support and resistance levels
def identify_support_resistance(df) -> pd.DataFrame, list, list:
    peaks_high, _ = find_peaks(df['High'], distance=20, prominence=df['High'].std())
    peaks_low, _ = find_peaks(-df['Low'], distance=20, prominence=df['Low'].std())

    resistance_levels = df['High'].iloc[peaks_high].nlargest(3).values
    support_levels = df['Low'].iloc[peaks_low].nsmallest(3).values
    return df, resistance_levels, support_levels

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

#Price with SMAs and Bollinger Bands
def add_price_chart(fig, df):
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode='lines', name='SMA 20', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='SMA 50', line=dict(color='orange')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], mode='lines', name='SMA 200', line=dict(color='green')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], mode='lines', name='Bollinger Upper', line=dict(color='red', dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], mode='lines', name='Bollinger Lower', line=dict(color='red', dash='dash')), row=1, col=1)

# add support and resistance levels
def add_support_resistance(fig, df, resistance_levels, support_levels):
    for level in resistance_levels:
        fig.add_trace(go.Scatter(x=df.index, y=[level]*len(df), mode='lines', name='Resistance', line=dict(color='red', dash='dot')), row=1, col=1)
    for level in support_levels:
        fig.add_trace(go.Scatter(x=df.index, y=[level]*len(df), mode='lines', name='Support', line=dict(color='green', dash='dot')), row=1, col=1)

# add volume
def add_volume_chart(fig, df):
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='lightblue'), row=2, col=1)

# add RSI
def add_rsi_chart(fig, df):
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI', line=dict(color='purple')), row=3, col=1)
    fig.add_hline(y=70, line=dict(color='red', dash='dash'), row=3, col=1)
    fig.add_hline(y=30, line=dict(color='green', dash='dash'), row=3, col=1)

# add MACD
def add_macd_chart(fig, df):
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(color='blue')), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], mode='lines', name='MACD Signal', line=dict(color='orange')), row=4, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name='MACD Histogram', marker_color='lightblue'), row=4, col=1)

# add ATR
def add_atr_chart(fig, df):
    fig.add_trace(go.Scatter(x=df.index, y=df['ATR'], mode='lines', name='ATR', line=dict(color='brown')), row=5, col=1)

def finalize_chart(fig):
    fig.update_layout(title='BTC Technical Analysis', xaxis_title='Date', yaxis_title='Price', height=1400, showlegend=False, xaxis_rangeslider_visible=False)
    fig.update_xaxes(title_text = "Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text = "Volume", row=2, col=1)
    fig.update_yaxes(title_text = "RSI", row=3, col=1)
    fig.update_yaxes(title_text = "MACD", row=4, col=1)
    fig.update_yaxes(title_text = "ATR", row=5, col=1)
    return fig


def main():
    btc = fetch_crypto_data('BTC-USD')
    btc = calculate_technical_indicators(btc)
    btc = calculate_bollinger_bands(btc)
    btc = calculate_rsi(btc)
    btc = calculate_macd(btc)
    btc = calculate_atr(btc)

    btc, btc_resistance_levels, btc_support_levels = identify_support_resistance(btc)
    print_values(btc, btc_resistance_levels, btc_support_levels)

    fig = create_comprehensive_chart()
    add_price_chart(fig, btc)
    add_support_resistance(fig, btc, btc_resistance_levels, btc_support_levels)
    add_volume_chart(fig, btc)
    add_rsi_chart(fig, btc)
    add_macd_chart(fig, btc)
    add_atr_chart(fig, btc)
    fig = finalize_chart(fig)
    fig.show()


if __name__ == "__main__":
    main()