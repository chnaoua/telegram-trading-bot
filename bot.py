import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== الإعدادات =====
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN غير موجود! أضفه في متغيرات البيئة")
    exit(1)

# ===== البيانات =====
EXCHANGES = {
    "binance": {"name": "Binance", "icon": "🟡"},
    "bybit": {"name": "Bybit", "icon": "🔵"}
}

ASSET_TYPES = {
    "crypto": "العملات المشفرة 🪙",
    "forex": "العملات الأجنبية 💱",
    "stocks": "الأسهم 📈",
    "metals": "المعادن الثمينة 🥇"
}

CRYPTO_PAIRS = {
    "BTC/USDT": "Bitcoin",
    "ETH/USDT": "Ethereum",
    "SOL/USDT": "Solana",
    "BNB/USDT": "BNB",
    "XRP/USDT": "Ripple"
}

FOREX_PAIRS = {
    "EUR/USD": "Euro/US Dollar",
    "GBP/USD": "British Pound/US Dollar",
    "USD/JPY": "US Dollar/Japanese Yen"
}

STOCKS = {
    "AAPL": "Apple Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corp.",
    "TSLA": "Tesla Inc."
}

METALS = {
    "XAU/USD": "Gold (الذهب)",
    "XAG/USD": "Silver (الفضة)"
}

TRADING_TYPES = {
    "spot": "فوري (Spot)",
    "futures": "عقود مستقبلية (Futures)",
    "perp": "عقود دائمة (Perpetual)"
}

TIMEFRAMES = {
    "1m": "دقيقة واحدة ⏱️",
    "5m": "5 دقائق ⏱️",
    "15m": "15 دقيقة ⏱️",
    "30m": "30 دقيقة ⏱️",
    "1h": "ساعة واحدة 🕐",
    "4h": "4 ساعات 🕓",
    "1d": "يومي 📅",
    "1w": "أسبوعي 📆"
}

# ===== دوال البوت =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب"""
    user = update.effective_user
    
    welcome_text = f"""
🎯 **مرحباً بك في بوت التحليل الاحترافي!**

أهلاً {user.first_name} 👋

**للبدء، اختر خياراً من القائمة:**
    """
    
    keyboard = [
        [InlineKeyboardButton("📊 تحليل جديد", callback_data="new_analysis")],
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
    elif query.data == "help":
        await show_help(update, context)
    elif query.data == "settings":
        await show_settings(update, context)
    elif query.data == "main_menu":
        await main_menu(update, context)

# ===== الخطوة 1: اختيار المنصة =====
async def select_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اختيار المنصة"""
    keyboard = []
    for key, value in EXCHANGES.items():
        button_text = f"{value['icon']} {value['name']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"exchange_{key}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🏛️ **اختر المنصة:**",
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
    
    keyboard = []
    for key, value in ASSET_TYPES.items():
        keyboard.append([InlineKeyboardButton(value, callback_data=f"assettype_{key}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="new_analysis")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ تم اختيار: **{EXCHANGES[exchange]['name']}**\n\n📌 **اختر نوع الأصل:**",
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
        f"✅ تم اختيار: **{ASSET_TYPES[asset_type]}**\n\n📊 **اختر الأصل:**",
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
        f"✅ تم اختيار: **{symbol}**\n\n📈 **اختر نوع التداول:**",
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
    
    keyboard = []
    for key, value in TIMEFRAMES.items():
        keyboard.append([InlineKeyboardButton(value, callback_data=f"tf_{key}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="new_analysis")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ تم اختيار: **{TRADING_TYPES[trade_type]}**\n\n⏰ **اختر الفريم الزمني:**",
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
    
    # عرض ملخص وبدء التحليل
    summary = f"""
✅ **اكتملت الإعدادات!**

📌 **ملخص التحليل:**
• المنصة: {context.user_data.get('exchange', '')}
• نوع الأصل: {context.user_data.get('asset_type', '')}
• الأصل: {context.user_data.get('symbol', '')}
• نوع التداول: {context.user_data.get('trade_type', '')}
• الفريم: {TIMEFRAMES[timeframe]}

⏳ **جاري التحليل...**
    """
    
    await query.edit_message_text(
        summary,
        parse_mode='Markdown'
    )
    
    # محاكاة التحليل (بدون بيانات حقيقية لتجنب الأخطاء)
    await perform_simple_analysis(update, context)

async def perform_simple_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحليل بسيط (للتجربة)"""
    symbol = context.user_data.get('symbol', 'BTC/USDT')
    timeframe = context.user_data.get('timeframe', '1h')
    
    analysis_text = f"""
📊 **نتيجة التحليل**

🔹 **الأصل:** {symbol}
🔹 **الفريم:** {TIMEFRAMES[timeframe]}

**📈 التحليل الفني:**
• الاتجاه العام: صاعد 📈
• مستوى الدعم: 42,500
• مستوى المقاومة: 44,200
• RSI: 62 (محايد)
• MACD: إشارة شراء

**🎯 التوصية:**
• نقطة الدخول: 43,000
• وقف الخسارة: 42,200
• جني الربح: 44,500

⚠️ **تنبيه:** هذا تحليل تجريبي. سيتم إضافة البيانات الحقيقية قريباً.
    """
    
    await update.callback_query.message.reply_text(
        analysis_text,
        parse_mode='Markdown'
    )
    
    # سؤال عن تحديثات
    keyboard = [
        [InlineKeyboardButton("🔄 تحليل جديد", callback_data="new_analysis")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        "✅ **اكتمل التحليل!**\n\nهل تريد تحليلاً آخر؟",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ===== المساعدة =====
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المساعدة"""
    help_text = """
❓ **المساعدة**

📖 **كيفية استخدام البوت:**

1️⃣ اضغط على **تحليل جديد**
2️⃣ اختر المنصة (Binance أو Bybit)
3️⃣ اختر نوع الأصل
4️⃣ اختر الأصل المطلوب
5️⃣ اختر نوع التداول
6️⃣ اختر الفريم الزمني
7️⃣ انتظر النتائج

📌 **المنصات المدعومة:**
• Binance
• Bybit

💡 **نصائح:**
• استخدم الفريمات الكبيرة للتوجه العام
• استخدم الفريمات الصغيرة للتوقيت
• دائماً استخدم وقف الخسارة
    """
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ===== الإعدادات =====
async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الإعدادات"""
    settings_text = """
⚙️ **الإعدادات**

🔹 **الإعدادات الحالية:**
• نسبة المخاطرة/العائد: 1:2
• عدد الشموع: 500
• اللغة: العربية

(قيد التطوير)
    """
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        settings_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ===== القائمة الرئيسية =====
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """العودة للقائمة الرئيسية"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📊 تحليل جديد", callback_data="new_analysis")],
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
    """معالج الأخطاء"""
    logger.error(f"خطأ: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ حدث خطأ. يرجى المحاولة مرة أخرى."
        )

# ===== تشغيل البوت =====
def main():
    """تشغيل البوت"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler, pattern="^(new_analysis|help|settings|main_menu)$"))
        application.add_handler(CallbackQueryHandler(exchange_handler, pattern="^exchange_"))
        application.add_handler(CallbackQueryHandler(asset_type_handler, pattern="^assettype_"))
        application.add_handler(CallbackQueryHandler(symbol_handler, pattern="^symbol_"))
        application.add_handler(CallbackQueryHandler(trading_type_handler, pattern="^trade_"))
        application.add_handler(CallbackQueryHandler(timeframe_handler, pattern="^tf_"))
        application.add_handler(CallbackQueryHandler(show_help, pattern="^help$"))
        application.add_handler(CallbackQueryHandler(show_settings, pattern="^settings$"))
        application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
        application.add_error_handler(error_handler)
        
        logger.info("🚀 تم تشغيل البوت بنجاح!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"فشل تشغيل البوت: {e}")
        raise

if __name__ == '__main__':
    main()
