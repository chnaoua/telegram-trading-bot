import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from config import BOT_TOKEN, EXCHANGES, ASSET_TYPES, CRYPTO_PAIRS, FOREX_PAIRS, STOCKS, METALS, TRADING_TYPES, TIMEFRAMES
from utils.exchanges import get_exchange_data
from utils.analysis import analyze_technical, analyze_fundamental, analyze_time
from utils.chart_generator import generate_charts
import asyncio

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== دوال البوت =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب والقائمة الرئيسية"""
    user = update.effective_user
    
    welcome_text = f"""
🎯 **مرحباً بك في بوت التحليل الاحترافي!**

أهلاً {user.first_name} 👋

هذا البوت يوفر تحليلاً دقيقاً للأسواق باستخدام:
📊 تحليل فني متقدم
📰 تحليل أساسي شامل
⏰ تحليل زمني دقيق
🤖 ذكاء اصطناعي لتحديد الدعم والمقاومة

**المنصات المدعومة:**
🟡 Binance
🔵 Bybit

**للبدء، اختر خياراً من القائمة:**
    """
    
    keyboard = [
        [InlineKeyboardButton("📊 تحليل جديد", callback_data="new_analysis")],
        [InlineKeyboardButton("📈 تحديثات تلقائية", callback_data="auto_updates")],
        [InlineKeyboardButton("❓ مساعدة", callback_data="help")],
        [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار الرئيسية"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "new_analysis":
        await select_exchange(update, context)
    elif query.data == "auto_updates":
        await manage_auto_updates(update, context)
    elif query.data == "help":
        await show_help(update, context)
    elif query.data == "settings":
        await show_settings(update, context)
    elif query.data == "main_menu":
        await main_menu(update, context)

# ===== الخطوة 1: اختيار المنصة =====
async def select_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اختيار المنصة (Binance أو Bybit)"""
    keyboard = []
    for key, value in EXCHANGES.items():
        button_text = f"{value['icon']} {value['name']} - {value['description']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"exchange_{key}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🏛️ **اختر المنصة:**

🟡 **Binance** - أكبر منصة للعملات المشفرة
🔵 **Bybit** - متخصصة في العقود المستقبلية

اختر المنصة التي ترغب في التحليل عليها:
    """
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# ===== الخطوة 2: اختيار نوع الأصل =====
async def exchange_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار المنصة"""
    query = update.callback_query
    await query.answer()
    
    exchange = query.data.replace("exchange_", "")
    context.user_data['exchange'] = exchange
    context.user_data['exchange_name'] = EXCHANGES[exchange]['name']
    
    keyboard = []
    for key, value in ASSET_TYPES.items():
        keyboard.append([InlineKeyboardButton(value, callback_data=f"assettype_{key}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="new_analysis")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ تم اختيار: **{EXCHANGES[exchange]['icon']} {EXCHANGES[exchange]['name']}**\n\n"
        "📌 **اختر نوع الأصل الذي تريد تحليله:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ===== الخطوة 3: اختيار الأصل =====
async def asset_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار نوع الأصل"""
    query = update.callback_query
    await query.answer()
    
    asset_type = query.data.replace("assettype_", "")
    context.user_data['asset_type'] = asset_type
    context.user_data['asset_type_name'] = ASSET_TYPES[asset_type]
    
    if asset_type == "crypto":
        assets = CRYPTO_PAIRS
    elif asset_type == "forex":
        assets = FOREX_PAIRS
    elif asset_type == "stocks":
        assets = STOCKS
    elif asset_type == "metals":
        assets = METALS
    else:
        assets = {}
    
    keyboard = []
    for symbol, name in assets.items():
        keyboard.append([InlineKeyboardButton(f"{symbol} - {name}", callback_data=f"symbol_{symbol}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="new_analysis")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ تم اختيار: **{ASSET_TYPES[asset_type]}**\n\n"
        "📊 **اختر الأصل الذي تريد تحليله:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ===== الخطوة 4: اختيار نوع التداول =====
async def symbol_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار رمز الأصل"""
    query = update.callback_query
    await query.answer()
    
    symbol = query.data.replace("symbol_", "")
    context.user_data['symbol'] = symbol
    
    keyboard = []
    for key, value in TRADING_TYPES.items():
        keyboard.append([InlineKeyboardButton(value, callback_data=f"trade_{key}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="new_analysis")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ تم اختيار: **{symbol}**\n\n"
        "📈 **اختر نوع التداول:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ===== الخطوة 5: اختيار الفريم =====
async def trading_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار نوع التداول"""
    query = update.callback_query
    await query.answer()
    
    trade_type = query.data.replace("trade_", "")
    context.user_data['trade_type'] = trade_type
    context.user_data['trade_type_name'] = TRADING_TYPES[trade_type]
    
    keyboard = []
    for key, value in TIMEFRAMES.items():
        keyboard.append([InlineKeyboardButton(value, callback_data=f"tf_{key}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="new_analysis")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ تم اختيار: **{TRADING_TYPES[trade_type]}**\n\n"
        "⏰ **اختر الفريم الزمني للتحليل:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ===== الخطوة 6: بدء التحليل =====
async def timeframe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار الفريم وبدء التحليل"""
    query = update.callback_query
    await query.answer()
    
    timeframe = query.data.replace("tf_", "")
    context.user_data['timeframe'] = timeframe
    context.user_data['timeframe_name'] = TIMEFRAMES[timeframe]
    
    # عرض رسالة جاري التحليل
    await query.edit_message_text(
        "⏳ **جاري تحليل البيانات...**\n\n"
        "🔄 يتم جلب البيانات من المنصة\n"
        "📊 حساب المؤشرات الفنية\n"
        "🎯 تحديد الدعم والمقاومة\n"
        "🤖 تطبيق الذكاء الاصطناعي\n\n"
        "يرجى الانتظار...",
        parse_mode='Markdown'
    )
    
    # تنفيذ التحليل
    await perform_full_analysis(update, context)

async def perform_full_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنفيذ التحليل الشامل وإرسال النتائج"""
    try:
        exchange = context.user_data.get('exchange')
        symbol = context.user_data.get('symbol')
        timeframe = context.user_data.get('timeframe')
        
        # جلب البيانات من المنصة
        data = await get_exchange_data(exchange, symbol, timeframe)
        
        if data is None or data.empty:
            await update.callback_query.message.reply_text(
                "❌ **فشل جلب البيانات**\n\n"
                "يرجى التأكد من:\n"
                "• صحة رمز الأصل\n"
                "• توفر البيانات على المنصة\n"
                "• اتصال الإنترنت\n\n"
                "حاول مرة أخرى لاحقاً.",
                parse_mode='Markdown'
            )
            return
        
        # ===== 1. إنشاء الرسوم البيانية =====
        chart_images = await generate_charts(data, symbol, context.user_data)
        
        # إرسال الرسم البياني الأول (الشارت العادي)
        if chart_images.get('basic'):
            await update.callback_query.message.reply_photo(
                photo=open(chart_images['basic'], 'rb'),
                caption=f"📊 **الشارت الأساسي**\n{symbol} - {TIMEFRAMES[timeframe]}"
            )
        
        # إرسال الرسم البياني الثاني (مع الدعم والمقاومة)
        if chart_images.get('analysis'):
            await update.callback_query.message.reply_photo(
                photo=open(chart_images['analysis'], 'rb'),
                caption=f"🎯 **التحليل مع الدعم والمقاومة**\n{symbol} - {TIMEFRAMES[timeframe]}"
            )
        
        # ===== 2. التحليل الفني =====
        technical = await analyze_technical(data)
        
        # ===== 3. التحليل الأساسي =====
        fundamental = await analyze_fundamental(symbol, exchange)
        
        # ===== 4. التحليل الزمني =====
        time_analysis = await analyze_time(data, timeframe)
        
        # ===== 5. إرسال النتائج (مقسمة) =====
        tech_text = f"""
📊 **التحليل الفني**

📌 **السعر الحالي:** {technical.get('current_price', 0)}
📈 **الاتجاه العام:** {technical.get('trend', 'غير محدد')}

**المؤشرات الفنية:**
• RSI (14): {technical.get('rsi', 0)} - {technical.get('rsi_signal', '')}
• MACD: {technical.get('macd', {}).get('signal', 'محايد')}
• المتوسط المتحرك 50: {technical.get('moving_averages', {}).get('sma_50', 0)}
• المتوسط المتحرك 200: {technical.get('moving_averages', {}).get('sma_200', 0)}

**مستويات الدعم والمقاومة:**
🟢 **الدعم:** {technical.get('support_resistance', {}).get('support', 0)}
🔴 **المقاومة:** {technical.get('support_resistance', {}).get('resistance', 0)}
🛑 **وقف الخسارة:** {technical.get('support_resistance', {}).get('stop_loss', 0)}
🎯 **جني الربح:** {technical.get('support_resistance', {}).get('take_profit', 0)}
        """
        await send_long_message(update, tech_text)
        
        fund_text = f"""
📰 **التحليل الأساسي**

{fundamental.get('summary', 'لا توجد بيانات كافية')}

**الأحداث المؤثرة:**
{chr(10).join([f'• {event}' for event in fundamental.get('events', ['لا توجد أحداث حالياً'])])}

**التوصية الأساسية:**
{fundamental.get('recommendation', 'محايد')}
        """
        await send_long_message(update, fund_text)
        
        time_text = f"""
⏰ **التحليل الزمني**

**أفضل أوقات التداول:**
{chr(10).join([f'• {time}' for time in time_analysis.get('best_times', ['غير متاح'])])}

**التوقيت الحالي:**
• الفريم: {TIMEFRAMES[timeframe]}
• عدد الشموع المحللة: {time_analysis.get('candles_count', 0)}
• التوقع الزمني: {time_analysis.get('prediction', 'محايد')}

**توصية التوقيت:**
{time_analysis.get('recommendation', 'انتظر تأكيداً إضافياً')}
        """
        await send_long_message(update, time_text)
        
        # ===== 6. سؤال عن التحديثات =====
        keyboard = [
            [InlineKeyboardButton("✅ تفعيل التحديثات التلقائية", callback_data="enable_updates")],
            [InlineKeyboardButton("🔄 تحليل جديد", callback_data="new_analysis")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.message.reply_text(
            "✅ **اكتمل التحليل!**\n\n"
            "هل ترغب في تفعيل التحديثات التلقائية؟\n"
            "ستتلقى تحليلات دورية حسب الفريم المختار.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"خطأ في التحليل: {e}")
        await update.callback_query.message.reply_text(
            f"❌ **حدث خطأ أثناء التحليل**\n\n{str(e)}",
            parse_mode='Markdown'
        )

async def send_long_message(update: Update, text: str, max_length: int = 4000):
    """إرسال رسائل طويلة مقسمة"""
    if len(text) <= max_length:
        await update.callback_query.message.reply_text(text, parse_mode='Markdown')
    else:
        parts = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        for part in parts:
            await update.callback_query.message.reply_text(part, parse_mode='Markdown')

# ===== دوال أخرى =====
async def manage_auto_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إدارة التحديثات التلقائية"""
    keyboard = [
        [InlineKeyboardButton("✅ تفعيل التحديثات", callback_data="enable_updates")],
        [InlineKeyboardButton("❌ إلغاء التحديثات", callback_data="disable_updates")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "📡 **التحديثات التلقائية**\n\n"
        "عند تفعيل هذه الميزة، ستتلقى تحليلات دورية:\n"
        "• حسب الفريم الزمني المختار\n"
        "• بناءً على آخر تحليل قمت به\n"
        "• تحديثات ذكية وليست عشوائية\n\n"
        "⚠️ تنبيه: التحديثات تتطلب بيانات حية من المنصة.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض رسالة المساعدة"""
    help_text = """
❓ **المساعدة والدعم**

📖 **كيفية استخدام البوت:**

1️⃣ اضغط على **تحليل جديد**
2️⃣ اختر المنصة (Binance أو Bybit)
3️⃣ اختر نوع الأصل (عملات مشفرة، فوركس، أسهم، معادن)
4️⃣ اختر الأصل المطلوب
5️⃣ اختر نوع التداول (فوري، عقود مستقبلية، عقود دائمة)
6️⃣ اختر الفريم الزمني
7️⃣ انتظر النتائج

📊 **ماذا يقدم التحليل؟**
• رسم بياني أساسي
• رسم بياني مع دعم ومقاومة
• تحليل فني شامل
• تحليل أساسي
• تحليل زمني
• توصيات بإدارة المخاطر

💡 **نصائح مهمة:**
• استخدم الفريمات الأكبر للتوجه العام (1d, 4h)
• استخدم الفريمات الأصغر للتوقيت (15m, 1h)
• لا تعتمد على تحليل واحد فقط
• دائماً استخدم وقف الخسارة

📌 **المنصات المدعومة:**
• Binance (جميع الأصول المشفرة)
• Bybit (عملات مشفرة + أسهم)
    """
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الإعدادات"""
    settings_text = """
⚙️ **الإعدادات**

🔹 **الإعدادات الحالية:**
• نسبة المخاطرة/العائد: 1:2
• عدد الشموع للتحليل: 500
• لغة التحليل: العربية
• التحديثات التلقائية: معطلة

🔹 **خيارات التعديل:**
• تغيير نسبة المخاطرة/العائد
• تغيير عدد الشموع
• تغيير لغة التقارير

(قيد التطوير - سيتم إضافة المزيد من الخيارات قريباً)
    """
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        settings_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """العودة إلى القائمة الرئيسية"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📊 تحليل جديد", callback_data="new_analysis")],
        [InlineKeyboardButton("📈 تحديثات تلقائية", callback_data="auto_updates")],
        [InlineKeyboardButton("❓ مساعدة", callback_data="help")],
        [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎯 **القائمة الرئيسية**\n\nاختر الخيار المناسب:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ===== معالج الأخطاء =====
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام"""
    logger.error(f"خطأ: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ **حدث خطأ غير متوقع**\n\n"
            "يرجى المحاولة مرة أخرى لاحقاً.",
            parse_mode='Markdown'
        )

# ===== تشغيل البوت =====
def main():
    """الدالة الرئيسية"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # معالج الأوامر
        application.add_handler(CommandHandler("start", start))
        
        # معالج الأزرار الرئيسية
        application.add_handler(CallbackQueryHandler(button_handler, pattern="^(new_analysis|auto_updates|help|settings|main_menu|enable_updates|disable_updates)$"))
        
        # معالج المنصة
        application.add_handler(CallbackQueryHandler(exchange_handler, pattern="^exchange_"))
        
        # معالج نوع الأصل
        application.add_handler(CallbackQueryHandler(asset_type_handler, pattern="^assettype_"))
        
        # معالج رمز الأصل
        application.add_handler(CallbackQueryHandler(symbol_handler, pattern="^symbol_"))
        
        # معالج نوع التداول
        application.add_handler(CallbackQueryHandler(trading_type_handler, pattern="^trade_"))
        
        # معالج الفريم الزمني
        application.add_handler(CallbackQueryHandler(timeframe_handler, pattern="^tf_"))
        
        # معالج الأخطاء
        application.add_error_handler(error_handler)
        
        logger.info("🚀 تم تشغيل البوت بنجاح!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"فشل تشغيل البوت: {e}")
        raise

if __name__ == '__main__':
    main()
