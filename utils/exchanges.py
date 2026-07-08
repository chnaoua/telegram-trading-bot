import ccxt
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def get_exchange_data(exchange_name: str, symbol: str, timeframe: str):
    """
    جلب بيانات الأسعار من المنصة المحددة
    
    Args:
        exchange_name (str): اسم المنصة (binance, bybit)
        symbol (str): رمز العملة
        timeframe (str): الفريم الزمني
    
    Returns:
        pd.DataFrame: بيانات الشموع
    """
    try:
        # إنشاء كائن المنصة
        if exchange_name == "binance":
            exchange = ccxt.binance({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
        elif exchange_name == "bybit":
            exchange = ccxt.bybit({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
        else:
            logger.error(f"منصة غير مدعومة: {exchange_name}")
            return None
        
        # تحويل الفريم إلى صيغة ccxt
        timeframe_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
            "1w": "1w"
        }
        
        ccxt_timeframe = timeframe_map.get(timeframe, "1h")
        
        # تحديد عدد الشموع
        limit_map = {
            "1m": 100,
            "5m": 100,
            "15m": 200,
            "30m": 200,
            "1h": 200,
            "4h": 200,
            "1d": 100,
            "1w": 52
        }
        limit = limit_map.get(timeframe, 200)
        
        # جلب البيانات
        logger.info(f"جلب بيانات {symbol} من {exchange_name}، الفريم: {ccxt_timeframe}")
        
        ohlcv = exchange.fetch_ohlcv(symbol, ccxt_timeframe, limit=limit)
        
        if not ohlcv:
            logger.warning(f"لا توجد بيانات لـ {symbol} على {exchange_name}")
            return None
        
        # تحويل إلى DataFrame
        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        # تحويل الطابع الزمني
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        logger.info(f"تم جلب {len(df)} شمعة لـ {symbol}")
        return df
    
    except ccxt.NetworkError as e:
        logger.error(f"خطأ في الشبكة: {e}")
        return None
    except ccxt.ExchangeError as e:
        logger.error(f"خطأ في المنصة: {e}")
        return None
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {e}")
        return None

async def get_symbols_from_exchange(exchange_name: str):
    """الحصول على قائمة الرموز المتاحة على المنصة"""
    try:
        if exchange_name == "binance":
            exchange = ccxt.binance()
        elif exchange_name == "bybit":
            exchange = ccxt.bybit()
        else:
            return []
        
        markets = exchange.load_markets()
        symbols = list(markets.keys())
        
        # تصفية الرموز التي تحتوي على USDT (للعملات المشفرة)
        crypto_symbols = [s for s in symbols if '/USDT' in s]
        
        return crypto_symbols[:50]  # إرجاع أول 50 رمز
    
    except Exception as e:
        logger.error(f"خطأ في جلب الرموز: {e}")
        return []

def format_symbol_for_exchange(symbol: str, exchange: str):
    """تنسيق رمز العملة حسب المنصة"""
    if exchange == "binance":
        return symbol.upper()
    elif exchange == "bybit":
        return symbol.upper()
    return symbol
