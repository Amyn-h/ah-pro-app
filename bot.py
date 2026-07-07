# =============================================================================
# A.H Pro AI - نسخه کامل با تلگرام + خودآموزی + TP
# =============================================================================

import requests
import json
import os
import time
import threading
from datetime import datetime
from collections import defaultdict

# ============================== تنظیمات تلگرام ==============================
TELEGRAM_BOT_TOKEN = "8925524031:AAFxJFkH7MT_52gHgvreYCqNqQyk2p5_5NU"
TELEGRAM_CHAT_ID = "7418129701"
TELEGRAM_ENABLED = True

# ============================== ۱۰ صرافی کامل ==============================
EXCHANGES = {
    "Binance": {"klines": "https://api.binance.com/api/v3/klines", "ticker": "https://api.binance.com/api/v3/ticker/price"},
    "Bybit": {"klines": "https://api.bybit.com/v5/market/kline", "ticker": "https://api.bybit.com/v5/market/tickers"},
    "OKX": {"klines": "https://www.okx.com/api/v5/market/candles", "ticker": "https://www.okx.com/api/v5/market/ticker"},
    "Gate.io": {"klines": "https://api.gateio.ws/api/v4/spot/candlesticks", "ticker": "https://api.gateio.ws/api/v4/spot/tickers"},
    "KuCoin": {"klines": "https://api.kucoin.com/api/v1/market/candles", "ticker": "https://api.kucoin.com/api/v1/market/orderbook/level1"},
    "Huobi": {"klines": "https://api.huobi.pro/market/history/kline", "ticker": "https://api.huobi.pro/market/detail/merged"},
    "Bitget": {"klines": "https://api.bitget.com/api/v2/mix/market/candles", "ticker": "https://api.bitget.com/api/v2/mix/market/ticker"},
    "MEXC": {"klines": "https://api.mexc.com/api/v3/klines", "ticker": "https://api.mexc.com/api/v3/ticker/price"},
    "Toobit": {"klines": "https://api.toobit.com/quote/v1/klines", "ticker": "https://api.toobit.com/quote/v1/ticker/24hr"},
    "BingX": {"klines": "https://api.bingx.com/openApi/swap/v2/quote/klines", "ticker": "https://api.bingx.com/openApi/swap/v2/quote/ticker"}
}

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT",
    "ADAUSDT", "LTCUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TRXUSDT",
    "MATICUSDT", "NEARUSDT", "SHIBUSDT", "UNIUSDT", "AAVEUSDT", "MKRUSDT",
    "ATOMUSDT", "FILUSDT", "APTUSDT", "ARBUSDT", "OPUSDT", "SUIUSDT"
]

MEMORY_FILE = "ah_ai_memory.json"
STATS_FILE = "ah_ai_stats.json"
TP_FILE = "ah_ai_tp.json"

# ============================== توابع تلگرام ==============================
def send_telegram_message(message):
    if not TELEGRAM_ENABLED:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print("✅ پیام به تلگرام ارسال شد!")
            return True
        print(f"❌ خطا در ارسال تلگرام: {r.text}")
        return False
    except Exception as e:
        print(f"❌ خطای تلگرام: {e}")
        return False

def send_signal_to_telegram(signal_data):
    symbol, signal, score, price = signal_data["symbol"], signal_data["signal"], signal_data["score"], signal_data["price"]
    buy_score, sell_score = signal_data["buy_score"], signal_data["sell_score"]
    emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
    emoji_text = "خرید" if signal == "BUY" else "فروش" if signal == "SELL" else "خنثی"
    msg = f"🚀 <b>سیگنال جدید A.H Pro AI</b>\n\n{emoji} <b>{symbol}</b>\n📊 سیگنال: <b>{emoji_text}</b> - {score}%\n💰 قیمت: <b>${price}</b>\n📈 قدرت خرید: {buy_score} | فروش: {sell_score}\n"
    tp_entry = next((s for s in tp_manager.tp_data["signals"] if s["symbol"] == symbol and s["signal"] == signal), None)
    if tp_entry:
        msg += f"\n🎯 <b>TP Targets:</b>\n   TP1: ${tp_entry['tp1']} (1%)\n   TP2: ${tp_entry['tp2']} (2%)\n   TP3: ${tp_entry['tp3']} (4%)\n   TP4: ${tp_entry['tp4']} (6%)\n   TP5: ${tp_entry['tp5']} (8%)\n"
    if "analyst_list" in signal_data:
        msg += f"\n🧠 تحلیلگران موافق: {', '.join(signal_data['analyst_list'])}"
    msg += f"\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    send_telegram_message(msg)

# ============================== سیستم TP ==============================
class TPManager:
    def __init__(self):
        self.tp_data = self.load()

    def load(self):
        if os.path.exists(TP_FILE):
            with open(TP_FILE, "r") as f:
                return json.load(f)
        return {"signals": [], "tp_hits": {}, "total_signals": 0}

    def save(self):
        with open(TP_FILE, "w") as f:
            json.dump(self.tp_data, f, indent=2)

    def add_signal(self, symbol, signal, price, analysts):
        entry = {
            "symbol": symbol, "signal": signal, "entry_price": price,
            "timestamp": datetime.now().isoformat(), "analysts": analysts,
            "tp1": round(price * (1.01 if signal == "BUY" else 0.99), 2),
            "tp2": round(price * (1.02 if signal == "BUY" else 0.98), 2),
            "tp3": round(price * (1.04 if signal == "BUY" else 0.96), 2),
            "tp4": round(price * (1.06 if signal == "BUY" else 0.94), 2),
            "tp5": round(price * (1.08 if signal == "BUY" else 0.92), 2),
            "hit_tp": [], "closed": False, "final_result": None, "max_profit": 0
        }
        self.tp_data["signals"].append(entry)
        self.tp_data["total_signals"] += 1
        self.save()
        return entry

    def check_signals(self, current_prices):
        for signal in self.tp_data["signals"]:
            if signal["closed"]:
                continue
            symbol = signal["symbol"]
            if symbol not in current_prices:
                continue
            current_price = current_prices[symbol]
            entry_price = signal["entry_price"]
            profit_pct = ((current_price - entry_price) / entry_price) * 100 if signal["signal"] == "BUY" else ((entry_price - current_price) / entry_price) * 100
            if profit_pct > signal["max_profit"]:
                signal["max_profit"] = profit_pct
            for tp_name, tp_pct in [("tp1", 1.0), ("tp2", 2.0), ("tp3", 4.0), ("tp4", 6.0), ("tp5", 8.0)]:
                if tp_name not in signal["hit_tp"] and profit_pct >= tp_pct:
                    signal["hit_tp"].append(tp_name)
                    self.tp_data["tp_hits"][tp_name] = self.tp_data["tp_hits"].get(tp_name, 0) + 1
                    send_telegram_message(f"✅ <b>{signal['symbol']}</b>\n🎯 {tp_name.upper()} رسیده شد!\n💰 سود: {profit_pct:.2f}%")
            if "tp5" in signal["hit_tp"] or profit_pct < -5:
                signal["closed"] = True
                signal["final_result"] = "WIN" if "tp5" in signal["hit_tp"] else "LOSS"
                for analyst in signal["analysts"]:
                    memory.update(analyst, signal["final_result"] == "WIN")
        self.save()

tp_manager = TPManager()

# ============================== حافظه و یادگیری خودکار ==============================
class AIMemory:
    def __init__(self):
        self.memory = self.load()
        self.accuracy = defaultdict(lambda: {"correct": 0, "wrong": 0, "total": 0})
        self.weights = defaultdict(lambda: 1.0)
        self.learning_interval = 5 * 3600
        self.load_stats()
        self.start_auto_learning()

    def load(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        return {"trades": [], "history": []}

    def save(self):
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.memory, f, indent=2)

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, "r") as f:
                data = json.load(f)
                for k, v in data.get("accuracy", {}).items():
                    self.accuracy[k] = v
                for k, v in data.get("weights", {}).items():
                    self.weights[k] = v

    def save_stats(self):
        with open(STATS_FILE, "w") as f:
            json.dump({"accuracy": dict(self.accuracy), "weights": dict(self.weights)}, f, indent=2)

    def update(self, analyst, correct):
        self.accuracy[analyst]["total"] += 1
        if correct:
            self.accuracy[analyst]["correct"] += 1
        else:
            self.accuracy[analyst]["wrong"] += 1
        total = self.accuracy[analyst]["total"]
        if total >= 3:
            acc = self.accuracy[analyst]["correct"] / total
            self.weights[analyst] = round(0.2 + (acc * 1.6), 2)
        self.save_stats()

    def get_weight(self, analyst):
        return self.weights.get(analyst, 1.0)

    def auto_learn(self):
        send_telegram_message("🧠 شروع یادگیری خودکار A.H Pro AI...")
        signals_to_check = [s for s in self.memory.get("trades", []) if not s.get("checked", False)]
        for signal in signals_to_check:
            actual = signal.get("actual")
            if actual:
                correct = signal.get("predicted") == actual
                for analyst in signal.get("analysts", []):
                    self.update(analyst, correct)
                signal["checked"] = True
        self.save()
        send_telegram_message(f"✅ یادگیری خودکار کامل شد! {len(signals_to_check)} سیگنال بررسی شد.")

    def start_auto_learning(self):
        def learn_loop():
            while True:
                time.sleep(self.learning_interval)
                self.auto_learn()
        threading.Thread(target=learn_loop, daemon=True).start()

memory = AIMemory()

# ============================== دریافت داده ==============================
def get_ohlcv(symbol, exchange="Binance", interval="1h", limit=50):
    try:
        if exchange == "Binance":
            r = requests.get(EXCHANGES["Binance"]["klines"], params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=10)
            if r.status_code != 200: return None, f"HTTP {r.status_code}"
            raw = r.json()
            return [{"time": c[0], "open": float(c[1]), "high": float(c[2]), "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])} for c in raw], None
        elif exchange == "Toobit":
            r = requests.get(EXCHANGES["Toobit"]["klines"], params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=10)
            if r.status_code != 200: return None, f"HTTP {r.status_code}"
            raw = r.json()
            if not isinstance(raw, list) or len(raw) == 0: return None, "داده خالی"
            return [{"time": c[0], "open": float(c[1]), "high": float(c[2]), "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])} for c in raw], None
        return None, "این صرافی در نسخه ساده‌شده پشتیبانی نمی‌شود (فقط Binance و Toobit)"
    except Exception as e:
        return None, str(e)

def get_current_prices(exchange="Binance", symbols=SYMBOLS):
    prices = {}
    for symbol in symbols:
        candles, err = get_ohlcv(symbol, exchange, "1h", 1)
        if not err and candles:
            prices[symbol] = candles[-1]["close"]
        time.sleep(0.05)
    return prices

# ============================== تحلیلگرها ==============================
def calculate_rsi(closes, period=14):
    if len(closes) < period + 1: return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    avg_gain, avg_loss = sum(gains[-period:]) / period, sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    return round(100 - (100 / (1 + avg_gain / avg_loss)), 2)

def find_swing_points(candles, lookback=5):
    highs, lows = [], []
    for i in range(lookback, len(candles) - lookback):
        window = candles[i - lookback:i + lookback + 1]
        current = candles[i]
        if current["high"] == max(c["high"] for c in window): highs.append(current["high"])
        if current["low"] == min(c["low"] for c in window): lows.append(current["low"])
    return highs, lows

def poursamadi(candles):
    closes = [c["close"] for c in candles]
    price, avg20, rsi = closes[-1], sum(closes[-20:]) / 20, calculate_rsi(closes)
    diff = abs((price - avg20) / avg20) * 100
    score = 5
    if diff < 2 and rsi < 30: score = 9
    elif diff < 2 and rsi < 50: score = 7
    elif diff > 2 and rsi > 70: score = 9
    elif diff > 2 and rsi > 50: score = 7
    elif diff > 2 and rsi <= 15: score = 1
    score = min(10, max(1, round(score * memory.get_weight("poursamadi"))))
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def brooks(candles):
    if len(candles) < 5: return {"score": 5, "direction": "NEUTRAL"}
    last, prev = candles[-1], candles[-2]
    body, full = abs(last["close"] - last["open"]), last["high"] - last["low"]
    if full == 0: return {"score": 5, "direction": "NEUTRAL"}
    upper, lower = last["high"] - max(last["open"], last["close"]), min(last["open"], last["close"]) - last["low"]
    score = 5
    if lower > 2 * body and lower > upper: score = 9
    elif upper > 2 * body and upper > lower: score = 1
    elif last["high"] <= prev["high"] and last["low"] >= prev["low"]:
        score = 7 if last["close"] > last["open"] else 3
    score = min(10, max(1, round(score * memory.get_weight("brooks"))))
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def dow_theory(candles):
    highs, lows = find_swing_points(candles)
    if len(highs) < 3 or len(lows) < 3: return {"score": 5, "direction": "NEUTRAL"}
    score = 5
    if highs[-1] > highs[-2] > highs[-3] and lows[-1] > lows[-2] > lows[-3]: score = 9
    if highs[-1] < highs[-2] < highs[-3] and lows[-1] < lows[-2] < lows[-3]: score = 1
    score = min(10, max(1, round(score * memory.get_weight("dow_theory"))))
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

def trend_line(candles):
    if len(candles) < 10: return {"score": 5, "direction": "NEUTRAL"}
    closes = [c["close"] for c in candles]
    score = 5
    if closes[-1] > closes[-5] > closes[-10]: score = 9
    if closes[-1] < closes[-5] < closes[-10]: score = 1
    score = min(10, max(1, round(score * memory.get_weight("trend_line"))))
    return {"score": score, "direction": "BUY" if score >= 7 else "SELL" if score <= 3 else "NEUTRAL"}

ANALYSTS = [poursamadi, brooks, dow_theory, trend_line]
ANALYST_NAMES = {"poursamadi": "پورسمعادی", "brooks": "بروکس", "dow_theory": "داو", "trend_line": "خط روند"}

def analyze_symbol(symbol, exchange="Binance"):
    candles, err = get_ohlcv(symbol, exchange, "1h", 50)
    if err or not candles: return None, err
    results, total_score, buy_score, sell_score = {}, 0, 0, 0
    for analyst in ANALYSTS:
        result = analyst(candles)
        results[analyst.__name__] = result
        total_score += result["score"]
        if result["direction"] == "BUY": buy_score += result["score"]
        elif result["direction"] == "SELL": sell_score += result["score"]

    if buy_score > sell_score:
        signal, score = "BUY", round((buy_score / total_score) * 100, 1)
        analyst_list = [n for n in results if results[n]["direction"] == "BUY"]
    elif sell_score > buy_score:
        signal, score = "SELL", round((sell_score / total_score) * 100, 1)
        analyst_list = [n for n in results if results[n]["direction"] == "SELL"]
    else:
        signal, score, analyst_list = "NEUTRAL", 50, []

    price = candles[-1]["close"]
    if signal != "NEUTRAL" and analyst_list:
        tp_manager.add_signal(symbol, signal, price, analyst_list)

    return {"symbol": symbol, "price": round(price, 2), "signal": signal, "score": score,
            "buy_score": round(buy_score, 1), "sell_score": round(sell_score, 1),
            "analysts": results, "weights": {n: memory.get_weight(n) for n in results}, "analyst_list": analyst_list}, None

def scan_all(exchange="Binance", symbols=None):
    symbols = symbols or SYMBOLS
    results, best_signal = [], None
    for i, sym in enumerate(symbols):
        print(f"🔄 اسکن {i+1}/{len(symbols)}: {sym}")
        res, err = analyze_symbol(sym, exchange)
        if err:
            print(f"   ❌ {err}")
            continue
        if res:
            results.append(res)
            if res["signal"] != "NEUTRAL" and (best_signal is None or res["score"] > best_signal["score"]):
                best_signal = res
        time.sleep(0.05)
    results.sort(key=lambda x: x["score"], reverse=True)
    if best_signal and best_signal["score"] > 60:
        send_signal_to_telegram(best_signal)
    memory.save(); memory.save_stats(); tp_manager.save()
    tp_manager.check_signals(get_current_prices(exchange, symbols))
    return results

def print_results(results):
    if not results:
        print("⚠️ هیچ سیگنالی پیدا نشد!")
        return
    best = results[0]
    emoji = "🟢" if best['signal'] == "BUY" else "🔴" if best['signal'] == "SELL" else "⚪"
    print(f"\n🏆 {emoji} {best['symbol']} | {best['signal']} - {best['score']}% | ${best['price']}")
    print("\n📋 نتایج:")
    for i, r in enumerate(results[:10], 1):
        e = "🟢" if r['signal'] == "BUY" else "🔴" if r['signal'] == "SELL" else "⚪"
        print(f"  {i}. {e} {r['symbol']} - {r['signal']} - {r['score']}%")

def show_stats():
    print("\n📊 آمار یادگیری:")
    for name, data in memory.accuracy.items():
        total = data["total"]
        if total > 0:
            acc = round((data["correct"] / total) * 100, 1)
            print(f"  • {ANALYST_NAMES.get(name, name)}: {acc}% ({data['correct']}/{total})")

def show_menu():
    print("\n📋 منو:\n  1. 🔍 اسکن\n  2. 📊 آمار یادگیری\n  3. 📨 تست تلگرام\n  4. ❌ خروج")
    return input("  انتخاب: ").strip()

def main():
    print("🧠 A.H Pro AI - نسخه ساده‌شده و پایدار\n")
    print("صرافی‌های موجود: 1. Binance   2. Toobit")
    choice = input("انتخاب صرافی (پیش‌فرض 1): ").strip()
    exchange = "Toobit" if choice == "2" else "Binance"

    while True:
        choice = show_menu()
        if choice == "1":
            print("\n🔍 شروع اسکن...")
            print_results(scan_all(exchange))
            input("\n⏎ Enter برای ادامه...")
        elif choice == "2":
            show_stats()
            input("\n⏎ Enter برای ادامه...")
        elif choice == "3":
            send_telegram_message("🧠 پیام تست از A.H Pro AI")
            input("\n⏎ Enter برای ادامه...")
        elif choice == "4":
            print("👋 خداحافظ!")
            break
        else:
            print("❌ انتخاب نامعتبر!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 خداحافظ!")
    except Exception as e:
        print(f"❌ خطا: {e}")
