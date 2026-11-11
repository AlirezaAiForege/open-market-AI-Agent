# راهنمای شروع OpenMarket AI Agent

نسخهٔ فعلی یک گزارش نمونهٔ آفلاین است. تحلیل واقعی بازار، مدل هوش مصنوعی و ارسال سفارش هنوز پیاده‌سازی نشده‌اند.

## اجرا در Codespaces

۱. در صفحهٔ مخزن، شاخهٔ `main` را انتخاب کن.
۲. از Code → Codespaces، محیط پروژه را باز کن.
۳. از Terminal → New Terminal، ترمینال را باز کن. دستورها را داخل فایل کد ننویس.
۴. از پوشهٔ اصلی پروژه دستورهای زیر را به‌ترتیب اجرا کن:

```bash
python -m pip install -e ".[dev]"
python -m openmarket_ai
python -m pytest
```

گزارش باید شامل `Mode: DEMO`، `Data status: NO_MARKET_DATA` و `Signal: ABSTAIN` باشد. تست‌ها باید بدون خطا تمام شوند. نصب اولیه به اینترنت نیاز دارد؛ اجرای گزارش آفلاین است.

۵. برای تغییر نام نمایشی نماد:

```bash
python -m openmarket_ai --symbol BTCUSD
```

این گزینه فقط برچسب را عوض می‌کند و دادهٔ بیت‌کوین دریافت نمی‌کند.

## اجرا روی کامپیوتر

Python نسخهٔ ۳٫۱۰ یا بالاتر لازم است. مخزن را دریافت کن و وارد پوشهٔ آن شو:

```bash
git clone https://github.com/AlirezaAiForege/open-market-AI-Agent.git
cd open-market-AI-Agent
python -m venv .venv
```

در ویندوز PowerShell، از Python همان محیط استفاده کن؛ نیازی به تغییر تنظیمات امنیتی PowerShell نیست:

```powershell
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m openmarket_ai
.venv\Scripts\python.exe -m pytest
```

در لینوکس یا macOS:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m openmarket_ai
python -m pytest
```

## بررسی تست خودکار GitHub

۱. وارد بخش Actions مخزن شو.
۲. اجرای Python tests مربوط به آخرین تغییر را باز کن.
۳. نتیجهٔ هر سه محیط باید سبز باشد: لینوکس با Python 3.10 و 3.14 و ویندوز با Python 3.14.
۴. اگر اجرا قرمز بود، بخش ناموفق را باز کن و متن خطا را بررسی کن. سبزشدن تست‌ها فقط سلامت این نسخهٔ ابتدایی را نشان می‌دهد، نه صحت پیش‌بینی بازار یا سودآوری.

## وضعیت توسعه

مرحلهٔ ۷: هستهٔ قابل نصب Python و گزارش نمونه.
مرحلهٔ ۸: تست خودکار، بررسی ساخت بسته و راهنمای اجرا.
قدم بعد: واردکردن دادهٔ تاریخی از فایل CSV، اعتبارسنجی زمان و قیمت، و ثبت منبع و مجوز داده. انتخاب و اتصال منبع دادهٔ واقعی هنوز انجام نشده است.
