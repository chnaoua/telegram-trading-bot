import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

async def generate_charts(data: pd.DataFrame, symbol: str, user_data: dict):
    """إنشاء الرسوم البيانية"""
    try:
        charts = {}
        
        # إنشاء مجلد للصور إذا لم يكن موجوداً
        os.makedirs('charts', exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"charts/{symbol}_{timestamp}"
        
        # ===== 1. الرسم البياني الأساسي =====
        basic_chart = f"{base_filename}_basic.png"
        
        # إعدادات الرسم
        style = mpf.make_mpf_style(
            base_mpf_style='charles',
            gridstyle='',
            y_on_right=False,
            marketcolors=mpf.make_marketcolors(up='#26a69a', down='#ef5350', wick={'up':'#26a69a', 'down':'#ef5350'}, edge='inherit', volume='in')
        )
        
        # إنشاء الرسم البياني الأساسي
        mpf.plot(
            data.tail(100),
            type='candle',
            style=style,
            title=f'{symbol} - Price Chart',
            ylabel='Price',
            volume=True,
            figsize=(12, 8),
            savefig=basic_chart,
            show_nontrading=False
        )
        
        charts['basic'] = basic_chart
        
        # ===== 2. الرسم البياني مع التحليل =====
        analysis_chart = f"{base_filename}_analysis.png"
        
        # حساب الدعم والمقاومة
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # استخدام النقاط العالية والمنخفضة
        window = 20
        resistance = high.rolling(window=window, center=True).max()
        support = low.rolling(window=window, center=True).min()
        
        # إنشاء قائمة بالمؤشرات الإضافية
        apds = []
        
        # إضافة الدعم والمقاومة
        if not support.isna().all():
            apds.append(mpf.make_addplot(support, color='green', width=0.5, label='Support'))
        if not resistance.isna().all():
            apds.append(mpf.make_addplot(resistance, color='red', width=0.5, label='Resistance'))
        
        # إضافة المتوسطات المتحركة
        sma_20 = close.rolling(window=20).mean()
        sma_50 = close.rolling(window=50).mean()
        
        if not sma_20.isna().all():
            apds.append(mpf.make_addplot(sma_20, color='blue', width=0.5, label='MA 20'))
        if not sma_50.isna().all():
            apds.append(mpf.make_addplot(sma_50, color='orange', width=0.5, label='MA 50'))
        
        # إنشاء الرسم البياني مع التحليل
        mpf.plot(
            data.tail(100),
            type='candle',
            style=style,
            title=f'{symbol} - Analysis with Support/Resistance',
            ylabel='Price',
            volume=True,
            addplot=apds,
            figsize=(12, 10),
            savefig=analysis_chart,
            show_nontrading=False
        )
        
        charts['analysis'] = analysis_chart
        
        logger.info(f"تم إنشاء الرسوم البيانية لـ {symbol}")
        return charts
    
    except Exception as e:
        logger.error(f"خطأ في إنشاء الرسوم البيانية: {e}")
        return {}

def add_ai_analysis_to_chart(data: pd.DataFrame, support_levels: list, resistance_levels: list, filename: str):
    """إضافة تحليل الذكاء الاصطناعي إلى الرسم البياني"""
    try:
        # هذه دالة مستقبلية لتطبيق تحليل AI
        # يمكن إضافة نماذج تعلم آلي لتحديد المناطق بشكل أكثر دقة
        pass
    except Exception as e:
        logger.error(f"خطأ في إضافة تحليل AI: {e}")
