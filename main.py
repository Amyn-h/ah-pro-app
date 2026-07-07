# =============================================================================
# A.H Pro - نسخه نهایی با صفحه کاربری حرفه‌ای + ۱۰ تحلیلگر + ۱۰ صرافی
# =============================================================================

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
import threading
import requests
import json
import os
import time
from datetime import datetime

# ============================== تنظیمات ظاهری ==============================
Window.clearcolor = (0.05, 0.02, 0.08, 1)
Window.size = (400, 700)

# ============================== ۱۰ صرافی ==============================
EXCHANGES = {
    "Binance": {
        "klines": "https://api.binance.com/api/v3/klines",
        "ticker": "https://api.binance.com/api/v3/ticker/price",
        "color": "#F3BA2F"
    },
    "Bybit": {
        "klines": "https://api.bybit.com/v5/market/kline",
        "ticker": "https://api.bybit.com/v5/market/tickers",
        "color": "#F7A600"
    },
    "OKX": {
        "klines": "https://www.okx.com/api/v5/market/candles",
        "ticker": "https://www.okx.com/api/v5/market/ticker",
        "color": "#4A7CF7"
    },
    "Gate.io": {
        "klines": "https://api.gateio.ws/api/v4/spot/candlesticks",
        "ticker": "https://api.gateio.ws/api/v4/spot/tickers",
        "color": "#17A8FD"
    },
    "KuCoin": {
        "klines": "https://api.kucoin.com/api/v1/market/candles",
        "ticker": "https://api.kucoin.com/api/v1/market/orderbook/level1",
        "color": "#26A69A"
    },
    "Huobi": {
        "klines": "https://api.huobi.pro/market/history/kline",
        "ticker": "https://api.huobi.pro/market/detail/merged",
        "color": "#2C3E50"
    },
    "Bitget": {
        "klines": "https://api.bitget.com/api/v2/mix/market/candles",
        "ticker": "https://api.bitget.com/api/v2/mix/market/ticker",
        "color": "#2E7D32"
    },
    "MEXC": {
        "klines": "https://api.mexc.com/api/v3/klines",
        "ticker": "https://api.mexc.com/api/v3/ticker/price",
        "color": "#FF6B00"
    },
    "Toobit": {
        "klines": "https://api.toobit.com/quote/v1/klines",
        "ticker": "https://api.toobit.com/quote/v1/ticker/24hr",
        "color": "#7C3AED"
    },
    "BingX": {
        "klines": "https://api.bingx.com/openApi/swap/v2/quote/klines",
        "ticker": "https://api.bingx.com/openApi/swap/v2/quote/ticker",
        "color": "#00B4D8"
    }
}

# ============================== ۲۴ ارز ==============================
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT",
    "ADAUSDT", "LTCUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TRXUSDT",
    "MATICUSDT", "NEARUSDT", "SHIBUSDT", "UNIUSDT", "AAVEUSDT", "MKRUSDT",
    "ATOMUSDT", "FILUSDT", "APTUSDT", "ARBUSDT", "OPUSDT", "SUIUSDT"
]

STATS_FILE = "ah_scanner_stats.json"
USER_SYMBOLS_FILE = "user_symbols.json"

# ============================== توابع دریافت داده ==============================
def get_ohlcv(symbol, exchange="Binance", interval="1h", limit=50):
    try:
        if exchange == "Binance":
            params = {"symbol": symbol, "interval": interval, "limit": limit}
            r = requests.get(EXCHANGES["Binance"]["klines"], params=params, timeout=10)
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            raw = r.json()
            candles = []
            for c in raw:
                candles.append({
                    "time": c[0], "open": float(c[1]), "high": float(c[2]),
                    "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
                })
            return candles, None
            
        elif exchange == "Bybit":
            params = {"category": "linear", "symbol": symbol, "interval": interval, "limit": limit}
            r = requests.get(EXCHANGES["Bybit"]["klines"], params=params, timeout=10)
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            raw = r.json()
            if raw.get("retCode") != 0:
                return None, f"API Error: {raw.get('retMsg')}"
            candles = []
            for c in raw["result"]["list"]:
                candles.append({
                    "time": int(c[0]), "open": float(c[1]), "high": float(c[2]),
                    "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
                })
            return candles, None
            
        elif exchange == "OKX":
            params = {"instId": symbol, "bar": "1H", "limit": limit}
            r = requests.get(EXCHANGES["OKX"]["klines"], params=params, timeout=10)
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            raw = r.json()
            if raw.get("code") != "0":
                return None, f"API Error: {raw.get('msg')}"
            candles = []
            for c in raw["data"]:
                candles.append({
                    "time": int(c[0]), "open": float(c[1]), "high": float(c[2]),
                    "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
                })
            return candles, None
            
        elif exchange == "Gate.io":
            params = {"currency_pair": symbol, "interval": "1h", "limit": limit}
            r = requests.get(EXCHANGES["Gate.io"]["klines"], params=params, timeout=10)
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            raw = r.json()
            candles = []
            for c in raw:
                candles.append({
                    "time": int(c[0]), "open": float(c[1]), "high": float(c[2]),
                    "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
                })
            return candles, None
            
        elif exchange == "KuCoin":
            params = {"symbol": symbol, "type": "1hour", "limit": limit}
            r = requests.get(EXCHANGES["KuCoin"]["klines"], params=params, timeout=10)
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            raw = r.json()
            if raw.get("code") != "200000":
                return None, f"API Error: {raw.get('msg')}"
            candles = []
            for c in raw["data"]:
                candles.append({
                    "time": int(c[0]), "open": float(c[1]), "high": float(c[2]),
                    "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
                })
            return candles, None
            
        elif exchange == "Huobi":
            params = {"symbol": symbol.lower(), "period": "60min", "size": limit}
            r = requests.get(EXCHANGES["Huobi"]["klines"], params=params, timeout=10)
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            raw = r.json()
            if raw.get("status") != "ok":
                return None, f"API Error: {raw.get('err-msg')}"
            candles = []
            for c in raw["data"]:
                candles.append({
                    "time": c[0], "open": float(c[1]), "high": float(c[2]),
                    "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
                })
            return candles, None
            
        elif exchange == "Bitget":
            params = {"symbol": symbol, "granularity": "1H", "limit": limit}
            r = requests.get(EXCHANGES["Bitget"]["klines"], params=params, timeout=10)
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            raw = r.json()
            if raw.get("code") != "00000":
                return None, f"API Error: {raw.get('msg')}"
            candles = []
            for c in raw["data"]:
                candles.append({
                    "time": int(c[0]), "open": float(c[1]), "high": float(c[2]),
                    "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
                })
            return candles, None
            
        elif exchange == "MEXC":
            params = {"symbol": symbol, "interval": "1h", "limit": limit}
            r = requests.get(EXCHANGES["MEXC"]["klines"], params=params, timeout=10)
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            raw = r.json()
            candles = []
            for c in raw:
                candles.append({
                    "time": c[0], "open": float(c[1]), "high": float(c[2]),
                    "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
                })
            return candles, None
            
        elif exchange == "Toobit":
            params = {"symbol": symbol, "interval": interval, "limit": limit}
            r = requests.get(EXCHANGES["Toobit"]["klines"], params=params, timeout=10)
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            raw = r.json()
            if not isinstance(raw, list) or len(raw) == 0:
                return None, "داده خالی"
            candles = []
            for c in raw:
                candles.append({
                    "time": c[0], "open": float(c[1]), "high": float(c[2]),
                    "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
                })
            return candles, None
            
        elif exchange == "BingX":
            params = {"symbol": symbol, "interval": "1h", "limit": limit}
            r = requests.get(EXCHANGES["BingX"]["klines"], params=params, timeout=10)
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}"
            raw = r.json()
            if raw.get("code") != 0:
                return None, f"API Error: {raw.get('msg')}"
            candles = []
            for c in raw["data"]:
                candles.append({
                    "time": int(c[0]), "open": float(c[1]), "high": float(c[2]),
                    "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
                })
            return candles, None
            
        return None, "صرافی پشتیبانی نمی‌شود"
        
    except Exception as e:
        return None, str(e)

# ============================== ۱۰ تحلیلگر ==============================
def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def find_swing_points(candles, lookback=5):
    highs, lows = [], []
    for i in range(lookback, len(candles) - lookback):
        window = candles[i - lookback:i + lookback + 1]
        current = candles[i]
        if current["high"] == max(c["high"] for c in window):
            highs.append(current["high"])
        if current["low"] == min(c["low"] for c in window):
            lows.append(current["low"])
    return highs, lows

def poursamadi(candles):
    closes = [c["close"] for c in candles]
    price = closes[-1]
    avg20 = sum(closes[-20:]) / 20
    rsi = calculate_rsi(closes)
    diff = abs((price - avg20) / avg20) * 100
    
    score = 5
    if diff < 2 and rsi < 30:
        score = 9
    elif diff < 2 and rsi < 50:
        score = 7
    elif diff < 2 and rsi < 70:
        score = 5
    elif diff < 2 and rsi < 85:
        score = 3
    elif diff < 2 and rsi >= 85:
        score = 1
    elif diff > 2 and rsi > 70:
        score = 9
    elif diff > 2 and rsi > 50:
        score = 7
    elif diff > 2 and rsi > 30:
        score = 5
    elif diff > 2 and rsi > 15:
        score = 3
    elif diff > 2 and rsi <= 15:
        score = 1
    
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def brooks(candles):
    if len(candles) < 5:
        return {"score": 5, "direction": "NEUTRAL"}
    
    last, prev = candles[-1], candles[-2]
    body = abs(last["close"] - last["open"])
    full = last["high"] - last["low"]
    if full == 0:
        return {"score": 5, "direction": "NEUTRAL"}
    
    upper = last["high"] - max(last["open"], last["close"])
    lower = min(last["open"], last["close"]) - last["low"]
    
    score = 5
    if lower > 2 * body and lower > upper:
        score = 9
    elif upper > 2 * body and upper > lower:
        score = 1
    elif last["high"] <= prev["high"] and last["low"] >= prev["low"]:
        if last["close"] > last["open"]:
            score = 7
        else:
            score = 3
    
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def classic_price_action(candles):
    if len(candles) < 3:
        return {"score": 5, "direction": "NEUTRAL"}
    
    last, prev = candles[-1], candles[-2]
    body = abs(last["close"] - last["open"])
    full = last["high"] - last["low"]
    if full == 0:
        return {"score": 5, "direction": "NEUTRAL"}
    
    upper = last["high"] - max(last["open"], last["close"])
    lower = min(last["open"], last["close"]) - last["low"]
    
    score = 5
    if lower > 2 * body and lower > upper:
        score = 9
    elif last["close"] > prev["high"]:
        score = 8
    elif last["close"] > last["open"] and lower > upper:
        score = 7
    if upper > 2 * body and upper > lower:
        score = 1
    elif last["close"] < prev["low"]:
        score = 2
    elif last["close"] < last["open"] and upper > lower:
        score = 3
    
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def dow_theory(candles):
    highs, lows = find_swing_points(candles)
    if len(highs) < 3 or len(lows) < 3:
        return {"score": 5, "direction": "NEUTRAL"}
    
    score = 5
    if highs[-1] > highs[-2] > highs[-3] and lows[-1] > lows[-2] > lows[-3]:
        score = 9
    elif highs[-1] > highs[-2] or lows[-1] > lows[-2]:
        score = 7
    if highs[-1] < highs[-2] < highs[-3] and lows[-1] < lows[-2] < lows[-3]:
        score = 1
    elif highs[-1] < highs[-2] or lows[-1] < lows[-2]:
        score = 3
    
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def japanese_candlestick(candles):
    if len(candles) < 3:
        return {"score": 5, "direction": "NEUTRAL"}
    
    last, prev, prev2 = candles[-1], candles[-2], candles[-3]
    score = 5
    if last["close"] > last["open"] and prev["close"] < prev["open"] and last["high"] > prev["high"]:
        score = 9
    elif last["close"] < last["open"] and prev["close"] > prev["open"] and last["low"] < prev["low"]:
        score = 1
    elif prev["close"] > prev2["close"] and last["close"] < prev["close"]:
        score = 7
    elif prev["close"] < prev2["close"] and last["close"] > prev["close"]:
        score = 3
    
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def pivot_points(candles):
    if len(candles) < 10:
        return {"score": 5, "direction": "NEUTRAL"}
    
    highs, lows = find_swing_points(candles)
    if not highs or not lows:
        return {"score": 5, "direction": "NEUTRAL"}
    
    last = candles[-1]
    score = 5
    if last["close"] > highs[-1] and last["close"] > lows[-1]:
        score = 9
    elif last["close"] > highs[-1] or last["close"] > lows[-1]:
        score = 7
    if last["close"] < lows[-1] and last["close"] < highs[-1]:
        score = 1
    elif last["close"] < lows[-1] or last["close"] < highs[-1]:
        score = 3
    
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def trend_line(candles):
    if len(candles) < 10:
        return {"score": 5, "direction": "NEUTRAL"}
    
    closes = [c["close"] for c in candles]
    score = 5
    if closes[-1] > closes[-5] and closes[-5] > closes[-10]:
        score = 9
    elif closes[-1] > closes[-5] or closes[-5] > closes[-10]:
        score = 7
    if closes[-1] < closes[-5] and closes[-5] < closes[-10]:
        score = 1
    elif closes[-1] < closes[-5] or closes[-5] < closes[-10]:
        score = 3
    
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def range_price_action(candles):
    if len(candles) < 20:
        return {"score": 5, "direction": "NEUTRAL"}
    
    high = max(c["high"] for c in candles[-20:])
    low = min(c["low"] for c in candles[-20:])
    last = candles[-1]
    mid = (high + low) / 2
    
    score = 5
    if last["close"] > high and last["close"] > low:
        score = 9
    elif last["close"] > mid:
        score = 7
    if last["close"] < low and last["close"] < high:
        score = 1
    elif last["close"] < mid:
        score = 3
    
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def volume_price_action(candles):
    if len(candles) < 20:
        return {"score": 5, "direction": "NEUTRAL"}
    
    volumes = [c["volume"] for c in candles]
    avg_vol = sum(volumes[-20:]) / 20
    last = candles[-1]
    
    score = 5
    if last["volume"] > avg_vol * 1.5 and last["close"] > last["open"]:
        score = 9
    elif last["volume"] > avg_vol * 1.2 and last["close"] > last["open"]:
        score = 7
    if last["volume"] > avg_vol * 1.5 and last["close"] < last["open"]:
        score = 1
    elif last["volume"] > avg_vol * 1.2 and last["close"] < last["open"]:
        score = 3
    
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def multi_timeframe(candles):
    if len(candles) < 30:
        return {"score": 5, "direction": "NEUTRAL"}
    
    last = candles[-1]
    avg10 = sum(c["close"] for c in candles[-10:]) / 10
    avg30 = sum(c["close"] for c in candles[-30:]) / 30
    
    score = 5
    if last["close"] > avg10 > avg30:
        score = 9
    elif last["close"] > avg10 or avg10 > avg30:
        score = 7
    if last["close"] < avg10 < avg30:
        score = 1
    elif last["close"] < avg10 or avg10 < avg30:
        score = 3
    
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

ANALYSTS = [
    poursamadi, brooks, classic_price_action, dow_theory,
    japanese_candlestick, pivot_points, trend_line,
    range_price_action, volume_price_action, multi_timeframe
]

# ============================== تحلیل ==============================
def analyze_symbol(symbol, exchange="Binance"):
    candles, err = get_ohlcv(symbol, exchange, "1h", 50)
    if err or not candles:
        return None, err

    results = {}
    total_score = 0
    buy_score = 0
    sell_score = 0
    
    for analyst in ANALYSTS:
        result = analyst(candles)
        results[analyst.__name__] = result
        total_score += result["score"]
        
        if result["direction"] == "BUY":
            buy_score += result["score"]
        elif result["direction"] == "SELL":
            sell_score += result["score"]

    if buy_score > sell_score:
        signal = "BUY"
        score = round((buy_score / total_score) * 100, 1)
    elif sell_score > buy_score:
        signal = "SELL"
        score = round((sell_score / total_score) * 100, 1)
    else:
        signal = "NEUTRAL"
        score = 50

    price = candles[-1]["close"]

    return {
        "symbol": symbol,
        "price": round(price, 2),
        "signal": signal,
        "score": score,
        "total_score": total_score,
        "buy_score": buy_score,
        "sell_score": sell_score,
        "analysts": results
    }, None

def scan_all(exchange="Binance", symbols=None):
    if symbols is None:
        symbols = SYMBOLS
    
    results = []
    total = len(symbols)
    for i, sym in enumerate(symbols):
        res, err = analyze_symbol(sym, exchange)
        if err:
            continue
        if res:
            results.append(res)
        time.sleep(0.05)
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

# ============================== رابط کاربری ==============================
class AHScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=10, **kwargs)
        
        # ========== HEADER ==========
        header = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        # آواتار هوش مصنوعی
        avatar = Label(text="🧠", font_size=40, color=(0.7, 0.3, 1, 1))
        header.add_widget(avatar)
        
        # عنوان
        title_box = BoxLayout(orientation='vertical', size_hint=(0.7, 1))
        title_box.add_widget(Label(text="A.H Pro", font_size=28, color=(0.9, 0.5, 1, 1), bold=True))
        title_box.add_widget(Label(text="🤖 هوش مصنوعی تریدر", font_size=12, color=(0.6, 0.6, 0.8, 1)))
        header.add_widget(title_box)
        
        # وضعیت آنلاین
        status_dot = Label(text="🟢", font_size=20, color=(0, 1, 0, 1))
        header.add_widget(status_dot)
        
        self.add_widget(header)
        
        # ========== STATUS BAR ==========
        self.status = Label(text="🔮 آماده اسکن", font_size=14, color=(0.7, 0.7, 0.9, 1),
                           size_hint=(1, 0.05))
        self.add_widget(self.status)
        
        # ========== CONTROLS ==========
        controls = BoxLayout(size_hint=(1, 0.1), spacing=8)
        
        # انتخاب صرافی
        self.exchange_spinner = Spinner(
            text='Binance',
            values=list(EXCHANGES.keys()),
            size_hint=(0.4, 1),
            background_color=(0.2, 0.1, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        controls.add_widget(self.exchange_spinner)
        
        # دکمه اسکن
        scan_btn = Button(
            text="🔍 اسکن",
            font_size=18,
            background_color=(0.5, 0.2, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        scan_btn.bind(on_press=self.start_scan)
        controls.add_widget(scan_btn)
        
        self.add_widget(controls)
        
        # ========== ADD SYMBOL ==========
        add_layout = BoxLayout(size_hint=(1, 0.07), spacing=8)
        self.symbol_input = TextInput(
            hint_text="➕ افزودن ارز",
            multiline=False,
            font_size=14,
            background_color=(0.1, 0.05, 0.2, 1),
            foreground_color=(1, 1, 1, 1)
        )
        add_layout.add_widget(self.symbol_input)
        
        add_btn = Button(
            text="➕",
            size_hint=(0.15, 1),
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=18
        )
        add_btn.bind(on_press=self.add_symbol)
        add_layout.add_widget(add_btn)
        
        self.add_widget(add_layout)
        
        # ========== RESULTS ==========
        scroll = ScrollView(size_hint=(1, 0.55))
        self.results_label = Label(
            text="📊 منتظر اسکن...\n\n💡 نکات:\n• صرافی مورد نظر رو انتخاب کن\n• دکمه اسکن رو بزن\n• ۱۰ تحلیلگر هوشمند فعال هستن",
            font_size=13,
            color=(0.8, 0.8, 0.9, 1),
            halign='left',
            valign='top'
        )
        self.results_label.bind(size=self.results_label.setter('text_size'))
        scroll.add_widget(self.results_label)
        self.add_widget(scroll)
        
        # ========== FOOTER ==========
        footer = BoxLayout(size_hint=(1, 0.05), spacing=5)
        footer.add_widget(Label(
            text=f"📊 {len(SYMBOLS)} ارز | ۱۰ تحلیلگر | ۱۰ صرافی",
            font_size=10,
            color=(0.4, 0.4, 0.6, 1)
        ))
        self.add_widget(footer)
        
        # متغیرها
        self.last_results = []
        self.is_scanning = False

    # ========== توابع ==========
    def start_scan(self, instance):
        if self.is_scanning:
            return
        self.is_scanning = True
        self.status.text = "🔄 در حال اسکن..."
        self.results_label.text = "⏳ لطفاً صبر کنید...\n\n🤖 تحلیلگران در حال بررسی بازار..."
        threading.Thread(target=self.scan_thread, daemon=True).start()

    def scan_thread(self):
        exchange = self.exchange_spinner.text
        results = scan_all(exchange)
        Clock.schedule_once(lambda dt: self.show_results(results), 0)

    def show_results(self, results):
        self.is_scanning = False
        self.last_results = results
        
        if not results:
            self.results_label.text = "⚠️ هیچ سیگنالی پیدا نشد.\n\n🔄 صرافی دیگه‌ای امتحان کن یا ارزهای بیشتری اضافه کن."
            self.status.text = "✅ اسکن کامل شد"
            return

        # بهترین سیگنال
        best = results[0]
        emoji = "🟢" if best['signal'] == "BUY" else "🔴" if best['signal'] == "SELL" else "⚪"
        
        output = f"🤖 {emoji} {best['symbol']}\n"
        output += f"📊 {best['signal']} - {best['score']}%\n"
        output += f"💰 ${best['price']}\n"
        output += f"📈 خرید: {best['buy_score']:.1f} | فروش: {best['sell_score']:.1f}\n"
        output += f"📊 صرافی: {self.exchange_spinner.text}\n"
        output += "─" * 40 + "\n\n"
        
        # ۵ تا برتر
        output += "📋 ۵ سیگنال برتر:\n"
        for i, r in enumerate(results[:5], 1):
            emoji = "🟢" if r['signal'] == "BUY" else "🔴" if r['signal'] == "SELL" else "⚪"
            output += f"{i}. {emoji} {r['symbol']} - {r['signal']} - {r['score']}%\n"
        
        # خلاصه
        buy = len([r for r in results if r['signal'] == 'BUY'])
        sell = len([r for r in results if r['signal'] == 'SELL'])
        output += f"\n📊 خرید: {buy} | فروش: {sell} | کل: {len(results)}"
        
        # تحلیلگر برتر
        if results:
            best_analyst = max(results[0]['analysts'].items(), key=lambda x: x[1]['score'])
            output += f"\n🏅 بهترین تحلیلگر: {best_analyst[0]}"
        
        self.results_label.text = output
        self.status.text = f"✅ اسکن کامل شد - {len(results)} سیگنال"

    def add_symbol(self, instance):
        symbol = self.symbol_input.text.strip().upper()
        if not symbol:
            self.status.text = "⚠️ لطفاً یه ارز وارد کن!"
            return
        
        if symbol not in SYMBOLS:
            SYMBOLS.append(symbol)
            self.symbol_input.text = ""
            self.status.text = f"✅ {symbol} اضافه شد!"
            # به‌روزرسانی فوتر
            self.children[-1].children[0].text = f"📊 {len(SYMBOLS)} ارز | ۱۰ تحلیلگر | ۱۰ صرافی"
        else:
            self.status.text = f"⚠️ {symbol} قبلاً وجود دارد!"

# ============================== اپلیکیشن ==============================
class AHApp(App):
    def build(self):
        return AHScreen()

if __name__ == "__main__":
    AHApp().run()
