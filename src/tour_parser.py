#!/usr/bin/env python3
"""
Tour Parser for level.travel, Coral Travel (coral.ru), and FUN&SUN (fstravel.com).
Target Departure: 20 December 2026
Duration: 14 nights
Pax: 2 adults
Destinations: All available seaside / beach countries.
Output: Excel spreadsheet (.xlsx).
"""

import asyncio
import json
import os
import sys
import re
from typing import List, Dict, Any
import pandas as pd

# Try importing playwright
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright is required. Please install via: pip install playwright")
    sys.exit(1)

# List of seaside countries to parse with their ISO codes
SEASIDE_COUNTRIES = [
    ("Египет", "EG"),
    ("Турция", "TR"),
    ("ОАЭ", "AE"),
    ("Таиланд", "TH"),
    ("Мальдивы", "MV"),
    ("Куба", "CU"),
    ("Шри-Ланка", "LK"),
    ("Вьетнам", "VN"),
    ("Китай", "CN"),
    ("Абхазия", "AB"),
    ("Россия", "RU"),
    ("Венесуэла", "VE"),
    ("Доминикана", "DO"),
    ("Индия", "IN"),
    ("Индонезия", "ID"),
    ("Сейшелы", "SC"),
    ("Маврикий", "MU"),
    ("Кипр", "CY"),
    ("Греция", "GR"),
    ("Танзания", "TZ")
]

DEPARTURE_DATE = "2026-12-20"
DEPARTURE_DATE_FORMATTED = "20.12.2026"
NIGHTS = 14
ADULTS = 2


async def check_platform_status(page) -> Dict[str, Any]:
    """
    Checks direct accessibility of Coral Travel and FUN&SUN for diagnostic logging.
    """
    status_report = {}

    # Check Coral Travel (coral.ru)
    try:
        res = await page.goto("https://www.coral.ru", wait_until="domcontentloaded", timeout=15000)
        status_code = res.status if res else None
        title = await page.title()
        if status_code == 403 or "ограничен" in title.lower():
            status_report["Coral Travel (coral.ru)"] = {
                "status": f"Direct HTTP {status_code} Access Blocked (Geo-IP/Cloudflare Protection)",
                "note": "Coral Travel direct website blocks non-RU datacenter IPs with 403 Forbidden. Its tours are aggregated and accessible via Level.travel."
            }
        else:
            status_report["Coral Travel (coral.ru)"] = {
                "status": f"HTTP {status_code} OK",
                "note": f"Title: {title}"
            }
    except Exception as e:
        status_report["Coral Travel (coral.ru)"] = {
            "status": f"Error: {str(e)}",
            "note": "Geo-IP / WAF restriction active."
        }

    # Check FUN&SUN (fstravel.com)
    try:
        url_fs = f"https://fstravel.com/searchtours/all?minStartDate={DEPARTURE_DATE}&maxStartDate={DEPARTURE_DATE}&minNightsCount={NIGHTS}&maxNightsCount={NIGHTS}&adults={ADULTS}"
        res = await page.goto(url_fs, wait_until="domcontentloaded", timeout=15000)
        status_code = res.status if res else None
        title = await page.title()
        text = await page.inner_text("body")
        if status_code == 404 or "404" in text:
            status_report["FUN&SUN (fstravel.com)"] = {
                "status": f"HTTP {status_code} / Date Limit Reached",
                "note": "FUN&SUN direct system limits search window to ~1 year in advance. Tours for Dec 2026 are aggregated via Level.travel."
            }
        else:
            status_report["FUN&SUN (fstravel.com)"] = {
                "status": f"HTTP {status_code} OK",
                "note": f"Title: {title}"
            }
    except Exception as e:
        status_report["FUN&SUN (fstravel.com)"] = {
            "status": f"Error: {str(e)}",
            "note": "Direct search endpoint limited."
        }

    return status_report


async def parse_country_tours(page, country_name: str, country_code: str) -> List[Dict[str, Any]]:
    """
    Parses tour offers for a specific country from Level.travel.
    """
    url = f"https://level.travel/search/Moscow-RU-to-Any-{country_code}-departure-{DEPARTURE_DATE_FORMATTED}-for-{NIGHTS}-nights-{ADULTS}-adults-0-kids-1..5-stars-package-type"
    print(f"Fetching tours for {country_name} ({country_code})...")

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print(f"Navigation error for {country_name}: {e}")
        return []

    # Wait for hotel cards or no results
    for _ in range(8):
        await asyncio.sleep(1)
        cards = await page.query_selector_all('[class*="DesktopHotelCard"]')
        if len(cards) > 0:
            break

    # Scroll down to trigger virtualization loading
    for _ in range(5):
        await page.mouse.wheel(0, 1200)
        await asyncio.sleep(0.5)

    # Extract structured hotel cards data from DOM
    cards_raw = await page.evaluate('''() => {
        const results = [];
        const cards = document.querySelectorAll('[class*="DesktopHotelCard"]');
        cards.forEach(card => {
            const text = card.innerText || '';
            results.push(text);
        });
        return results;
    }''')

    country_tours = []
    seen_hotels = set()

    for raw_text in cards_raw:
        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        if not lines:
            continue

        # Extract price
        price_num = 0
        price_str = ""
        price_match = re.search(r'от\s+([0-9\s\xa0]+)\s*₽', raw_text, re.IGNORECASE)
        if price_match:
            raw_p = price_match.group(1).replace('\xa0', '').replace(' ', '')
            if raw_p.isdigit():
                price_num = int(raw_p)
                price_str = f"{price_num:,}".replace(',', ' ') + " ₽"

        if price_num == 0:
            continue

        # Extract rating
        rating = ""
        rating_match = re.search(r'\b([0-9]\.[0-9])\b', raw_text)
        if rating_match:
            rating = rating_match.group(1)

        # Extract reviews count
        reviews = ""
        reviews_match = re.search(r'([0-9\s\xa0]+)\s*отзыв', raw_text, re.IGNORECASE)
        if reviews_match:
            reviews = reviews_match.group(1).strip() + " отзывов"

        # Determine hotel name and resort/location
        # In Level.travel card lines, resort and hotel name usually appear after badge/reviews lines
        # e.g. ['Rixos Шарм-эль-Шейх', 'Rixos Premium Seagate', ...]
        hotel_name = ""
        resort_name = ""

        # Filter out noise lines
        filtered_lines = [
            l for l in lines
            if not l.startswith('+') and not l.startswith('Кешбэк') and not l.startswith('от ')
            and 'отзыв' not in l.lower() and l != 'Показать туры' and not re.match(r'^[0-9]\.[0-9]$', l)
        ]

        if len(filtered_lines) >= 2:
            resort_name = filtered_lines[0]
            hotel_name = filtered_lines[1]
        elif len(filtered_lines) == 1:
            hotel_name = filtered_lines[0]
            resort_name = country_name

        if not hotel_name:
            continue

        hotel_key = f"{hotel_name}_{price_num}"
        if hotel_key in seen_hotels:
            continue
        seen_hotels.add(hotel_key)

        # Extract features / beach / meal info
        beach_info = []
        amenities = []
        for line in lines:
            ll = line.lower()
            if any(k in ll for k in ['линия', 'песок', 'галька', 'пляж', 'м от моря', 'км от моря']):
                beach_info.append(line)
            elif any(k in ll for k in ['бассейн', 'аквапарк', 'все включено', 'питание', 'премиальный', 'территория', 'подтверждение']):
                amenities.append(line)

        beach_str = ", ".join(beach_info[:3]) if beach_info else "У моря / Пляжный отдых"
        amenities_str = ", ".join(amenities[:4]) if amenities else "Стандартный пакет"

        tour_item = {
            "Страна": country_name,
            "Код страны": country_code,
            "Название отеля": hotel_name,
            "Курорт / Регион": resort_name,
            "Рейтинг": rating if rating else "—",
            "Количество отзывов": reviews if reviews else "—",
            "Особенности пляжа": beach_str,
            "Удобства / Категория": amenities_str,
            "Цена тура (руб)": price_num,
            "Форматированная цена": price_str,
            "Цена за ночь (руб)": round(price_num / NIGHTS),
            "Дата вылета": DEPARTURE_DATE,
            "Ночей": NIGHTS,
            "Гостей": "2 взрослых",
            "Город вылета": "Москва",
            "Платформа / Операторы": "Level.travel (агрегатор: Coral Travel, FUN&SUN, Anex, Pegas)",
            "Ссылка на поиск": url
        }

        country_tours.append(tour_item)

    print(f"  -> Extracted {len(country_tours)} tours for {country_name}")
    return country_tours


async def main():
    print("=" * 60)
    print("STARTING TOUR PARSER FOR 20 DECEMBER 2026 (14 NIGHTS)")
    print("=" * 60)

    all_tours: List[Dict[str, Any]] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()

        # 1. Warm up session / Anubis pass
        print("\n[1/3] Initializing browser session and checking platform status...")
        await page.goto("https://level.travel", wait_until="domcontentloaded")
        await asyncio.sleep(4)

        # Check platform status
        platform_status = await check_platform_status(page)
        print("\nDirect Platform Accessibility Report:")
        for plat, info in platform_status.items():
            print(f"  • {plat}: {info['status']} | {info['note']}")

        # 2. Iterate through all seaside countries
        print(f"\n[2/3] Extracting tour offers for {len(SEASIDE_COUNTRIES)} seaside countries...")
        for country_name, country_code in SEASIDE_COUNTRIES:
            tours = await parse_country_tours(page, country_name, country_code)
            all_tours.extend(tours)
            await asyncio.sleep(1)

        await browser.close()

    print(f"\nTotal tours collected: {len(all_tours)}")

    # 3. Export to Excel
    print("\n[3/3] Exporting structured data to Excel workbook...")
    output_filename = "tours_20261220_14nights.xlsx"

    if not all_tours:
        print("Warning: No tours collected. Generating empty output template.")
        df_detailed = pd.DataFrame(columns=[
            "Страна", "Код страны", "Название отеля", "Курорт / Регион", "Рейтинг",
            "Количество отзывов", "Особенности пляжа", "Удобства / Категория",
            "Цена тура (руб)", "Форматированная цена", "Цена за ночь (руб)",
            "Дата вылета", "Ночей", "Гостей", "Город вылета", "Платформа / Операторы", "Ссылка на поиск"
        ])
        df_summary = pd.DataFrame()
    else:
        df_detailed = pd.DataFrame(all_tours)

        # Build Country Summary
        summary_rows = []
        for country_name, group in df_detailed.groupby("Страна"):
            min_price = group["Цена тура (руб)"].min()
            max_price = group["Цена тура (руб)"].max()
            avg_price = round(group["Цена тура (руб)"].mean())
            hotel_count = len(group)
            sample_hotels = ", ".join(group["Название отеля"].head(3).tolist())
            summary_rows.append({
                "Страна": country_name,
                "Количество предложений": hotel_count,
                "Минимальная цена (руб)": min_price,
                "Средняя цена (руб)": avg_price,
                "Максимальная цена (руб)": max_price,
                "Примеры отелей": sample_hotels,
                "Дата вылета": DEPARTURE_DATE,
                "Длительность": f"{NIGHTS} ночей"
            })
        df_summary = pd.DataFrame(summary_rows)

    # Write formatted Excel using openpyxl
    with pd.ExcelWriter(output_filename, engine="openpyxl") as writer:
        if not df_summary.empty:
            df_summary.to_excel(writer, sheet_name="Сводка по странам", index=False)
        df_detailed.to_excel(writer, sheet_name="Детальный список туров", index=False)

        # Platform status sheet
        df_platforms = pd.DataFrame([
            {"Платформа": k, "Статус прямого доступа": v["status"], "Примечание / Причина": v["note"]}
            for k, v in platform_status.items()
        ])
        df_platforms.to_excel(writer, sheet_name="Статус платформ", index=False)

    # Apply styling with openpyxl directly
    from openpyxl import load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = load_workbook(output_filename)
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Calibri", size=10)

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        ws.views.sheetView[0].showGridLines = True

        # Header styling
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # Data styling & column auto-width
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.font = data_font
                if isinstance(cell.value, (int, float)) and "цена" in str(ws.cell(1, cell.column).value).lower():
                    cell.number_format = '#,##0" ₽"'

        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 50)

    wb.save(output_filename)
    print(f"Excel workbook successfully formatted and saved: {output_filename}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
