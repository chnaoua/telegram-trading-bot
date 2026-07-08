import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands
from datetime import datetime, timedelta
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
        
        # بولينجر باند
        bb = BollingerBands(close, window=20, window_dev=2)
        bb_upper = bb.bollinger_hband()
        bb_lower = bb.bollinger_lband()
        bb_middle = bb.bollinger_mavg()
        
        # تحديد الدعم والمقاومة
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
                "signal": "إشارة شراء 🟢" if macd_line.iloc[-1] > signal_line.iloc[-1] else "إشارة بيع 🔴" if macd_line.iloc[-1] < signal_line.iloc[-1] else "محايد ⚪"
            },
            "moving_averages": {
                "sma_20": round(sma_20.iloc[-1], 2) if not pd.isna(sma_20.iloc[-1]) else 0,
                "sma_50": round(sma_50.iloc[-1], 2) if not pd.isna(sma_50.iloc[-1]) else 0,
                "sma_200": round(sma_200.iloc[-1], 2) if not pd.isna(sma_200.iloc[-1]) else 0
            },
            "support_resistance": support_resistance,
            "volume": {
                "current": int(volume.iloc[-1]),
                "ratio": round(volume_ratio, 2),
                "signal": "حجم مرتفع 📊" if volume_ratio > 1.5 else "حجم متوسط" if volume_ratio > 0.8 else "حجم منخفض"
            }
        }
    
    except Exception as e:
        logger.error(f"خطأ في التحليل الفني: {e}")
        return {"error": str(e)}

def find_support_resistance(data: pd.DataFrame, window: int = 20):
    """العثور على مستويات الدعم والمقاومة"""
    try:
        close = data['Close']
        high = data['High']
        low = data['Low']
        
        # استخدام النقاط العالية والمنخفضة
        resistance = high.rolling(window=window, center=True).max()
        support = low.rolling(window=window, center=True).min()
        
        current_resistance = resistance.iloc[-1] if not pd.isna(resistance.iloc[-1]) else close.iloc[-1] * 1.05
        current_support = support.iloc[-1] if not pd.isna(support.iloc[-1]) else close.iloc[-1] * 0.95
        
        # حساب نقاط الارتكاز
        pivot = (high.iloc[-1] + low.iloc[-1] + close.iloc[-1]) / 3
        r1 = 2 * pivot - low.iloc[-1]
        s1 = 2 * pivot - high.iloc[-1]
        
        return {
            "support": round(current_support, 2),
            "resistance": round(current_resistance, 2),
            "pivot": round(pivot, 2),
            "r1": round(r1, 2),
            "s1": round(s1, 2),
            "stop_loss": round(current_support * 0.99, 2),
            "take_profit": round(current_resistance * 1.02, 2)
        }
    
    except Exception as e:
        logger.error(f"خطأ في تحديد الدعم والمقاومة: {e}")
        return {
            "support": 0,
            "resistance": 0,
            "stop_loss": 0,
            "take_profit": 0
        }

async def analyze_fundamental(symbol: str, exchange: str):
    """التحليل الأساسي (محاكاة)"""
    try:
        # في الواقع، هنا ستجلب البيانات من مصادر أخبار أو APIs
        # هذا مجرد مثال توضيحي
        events = []
        
        # محاكاة أحداث مؤثرة
        if "BTC" in symbol:
            events.append("تحديثات حول سياسات الاحتياطي الفيدرالي قد تؤثر على BTC")
            events.append("نشاط كبير في صناديق BTC المتداولة")
        elif "ETH" in symbol:
            events.append("تحديثات شبكة Ethereum والتطبيقات اللامركزية")
        else:
            events.append("لا توجد أحداث رئيسية حالياً")
        
        return {
            "summary": f"تحليل أساسي لـ {symbol} - السوق في حالة استقرار نسبي",
            "events": events,
            "recommendation": "محايد - انتظر تأكيدات إضافية"
        }
    
    except Exception as e:
        logger.error(f"خطأ في التحليل الأساسي: {e}")
        return {
            "summary": "لا توجد بيانات كافية للتحليل الأساسي",
            "events": ["غير متاح"],
            "recommendation": "محايد"
        }

async def analyze_time(data: pd.DataFrame, timeframe: str):
    """التحليل الزمني"""
    try:
        if data.empty:
            return {"error": "لا توجد بيانات"}
        
        # تحليل أفضل أوقات التداول (محاكاة)
        best_times = []
        
        if timeframe in ["1m", "5m", "15m"]:
            best_times.append("ساعات التداول الأوروبية (8 صباحاً - 4 مساءً)")
            best_times.append("ساعات التداول الأمريكية (2 ظهراً - 10 مساءً)")
        elif timeframe in ["1h", "4h"]:
            best_times.append("افتتاح السوق الأمريكية (2:30 مساءً)")
            best_times.append("إغلاق السوق الأوروبية (4 مساءً)")
        else:
            best_times.append("بداية الأسبوع (الأحد/الإثنين)")
            best_times.append("منتصف الأسبوع (الأربعاء/الخميس)")
        
        return {
            "best_times": best_times,
            "candles_count": len(data),
            "prediction": "استقرار مع احتمالية تحرك خلال 24 ساعة",
            "recommendation": "تابع تحركات السوق خلال الساعات القادمة"
        }
    
    except Exception as e:
        logger.error(f"خطأ في التحليل الزمني: {e}")
        return {
            "best_times": ["غير متاح"],
            "candles_count": 0,
            "prediction": "غير محدد",
            "recommendation": "انتظر"
        }
