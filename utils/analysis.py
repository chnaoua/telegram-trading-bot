import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands
import logging

logger = logging.getLogger(__name__)

async def analyze_technical(data: pd.DataFrame):
    """التحليل الفني الشامل"""
    try:
        if data.empty:
            return {"error": "لا توجد بيانات كافية"}
        
        close = data['Close']
        high = data['High']
        low = data['Low']
        volume = data['Volume']
        
        # RSI
        rsi = RSIIndicator(close, window=14).rsi()
        current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
        
        # MACD
        macd = MACD(close)
        macd_line = macd.macd()
        signal_line = macd.macd_signal()
        
        # المتوسطات المتحركة
        sma_20 = SMAIndicator(close, window=20).sma_indicator()
        sma_50 = SMAIndicator(close, window=50).sma_indicator()
        sma_200 = SMAIndicator(close, window=200).sma_indicator()
        ema_20 = EMAIndicator(close, window=20).ema_indicator()
        ema_50 = EMAIndicator(close, window=50).ema_indicator()
        
        # بولينجر باند
        bb = BollingerBands(close, window=20, window_dev=2)
        bb_upper = bb.bollinger_hband()
        bb_lower = bb.bollinger_lband()
        bb_middle = bb.bollinger_mavg()
        
        # الدعم والمقاومة
        support_resistance = find_support_resistance(data)
        
        # الاتجاه العام
        if close.iloc[-1] > sma_50.iloc[-1]:
            trend = "صاعد 📈"
        elif close.iloc[-1] < sma_50.iloc[-1]:
            trend = "هابط 📉"
        else:
            trend = "جانبي ➡️"
        
        # تحليل حجم التداول
        avg_volume = volume.rolling(window=20).mean()
        volume_ratio = volume.iloc[-1] / avg_volume.iloc[-1] if avg_volume.iloc[-1] > 0 else 1
        
        return {
            "current_price": round(close.iloc[-1], 2),
            "trend": trend,
            "rsi": round(current_rsi, 2),
            "rsi_signal": "ذروة شراء 🔴" if current_rsi > 70 else "ذروة بيع 🟢" if current_rsi < 30 else "محايد ⚪",
            "macd": {
                "macd_line": round(macd_line.iloc[-1], 4) if not pd.isna(macd_line.iloc[-1]) else 0,
                "signal_line": round(signal_line.iloc[-1], 4) if not pd.isna(signal_line.iloc[-1]) else 0,
                "signal": "إشارة شراء 🟢" if macd_line.iloc[-1] > signal_line.iloc[-1] else "إشارة بيع 🔴" if macd_line.iloc[-1] < signal_line.iloc[-1] else "محايد ⚪"
            },
            "moving_averages": {
                "sma_20": round(sma_20.iloc[-1], 2) if not pd.isna(sma_20.iloc[-1]) else 0,
                "sma_50": round(sma_50.iloc[-1], 2) if not pd.isna(sma_50.iloc[-1]) else 0,
                "sma_200": round(sma_200.iloc[-1], 2) if not pd.isna(sma_200.iloc[-1]) else 0,
                "ema_20": round(ema_20.iloc[-1], 2) if not pd.isna(ema_20.iloc[-1]) else 0,
                "ema_50": round(ema_50.iloc[-1], 2) if not pd.isna(ema_50.iloc[-1]) else 0
            },
            "bollinger_bands": {
                "upper": round(bb_upper.iloc[-1], 2) if not pd.isna(bb_upper.iloc[-1]) else 0,
                "middle": round(bb_middle.iloc[-1], 2) if not pd.isna(bb_middle.iloc[-1]) else 0,
                "lower": round(bb_lower.iloc[-1], 2) if not pd.isna(bb_lower.iloc[-1]) else 0,
                "position": "أعلى النطاق" if close.iloc[-1] > bb_upper.iloc[-1] else "أسفل النطاق" if close.iloc[-1] < bb_lower.iloc[-1] else "داخل النطاق"
            },
            "support_resistance": support_resistance,
            "volume": {
                "current": int(volume.iloc[-1]),
                "ratio": round(volume_ratio, 2),
                "signal": "حجم مرتفع 📊" if volume_ratio > 1.5 else "حجم متوسط" if volume
