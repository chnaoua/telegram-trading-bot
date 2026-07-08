import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

EXCHANGES = {
    "binance": {
        "name": "Binance",
        "icon": "🟡",
        "description": "أكبر منصة للعملات المشفرة"
    },
    "bybit": {
        "name": "Bybit",
        "icon": "🔵",
        "description": "منصة متخصصة في العقود المستقبلية"
    }
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
    "XRP/USDT": "Ripple",
    "ADA/USDT": "Cardano",
    "DOT/USDT": "Polkadot",
    "AVAX/USDT": "Avalanche",
    "MATIC/USDT": "Polygon",
    "LINK/USDT": "Chainlink"
}

FOREX_PAIRS = {
    "EUR/USD": "Euro/US Dollar",
    "GBP/USD": "British Pound/US Dollar",
    "USD/JPY": "US Dollar/Japanese Yen",
    "AUD/USD": "Australian Dollar/US Dollar",
    "USD/CHF": "US Dollar/Swiss Franc",
    "USD/CAD": "US Dollar/Canadian Dollar"
}

STOCKS = {
    "AAPL": "Apple Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corp.",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla Inc.",
    "NVDA": "NVIDIA Corp.",
    "META": "Meta Platforms Inc.",
    "NFLX": "Netflix Inc."
}

METALS = {
    "XAU/USD": "Gold (الذهب)",
    "XAG/USD": "Silver (الفضة)",
    "XPT/USD": "Platinum (البلاتين)",
    "XPD/USD": "Palladium (البلاديوم)"
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
