import argparse
import json
import random
import os
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from PIL import Image, ImageFilter, ImageEnhance

# ---------------------------------------------------------------------------
# Configuration: Australian energy market data
# ---------------------------------------------------------------------------

RETAILERS = {
    "AGL": {
        "color": colors.HexColor("#003D7A"),
        "accent": colors.HexColor("#EE2E24"),
        "logo_text": "AGL",
        "tagline": "Energy in motion",
        "states": ["NSW", "VIC", "QLD", "SA"],
        "abn": "74 115 061 375",
        "address": "AGL Energy Limited, Level 24, 200 George St, Sydney NSW 2000",
    },
    "Origin": {
        "color": colors.HexColor("#000F44"),
        "accent": colors.HexColor("#F26C21"),
        "logo_text": "Origin",
        "tagline": "Energy for life",
        "states": ["NSW", "VIC", "QLD", "SA", "ACT"],
        "abn": "33 010 328 119",
        "address": "Origin Energy Limited, Level 32, Tower 1, 100 Barangaroo Ave, Sydney NSW 2000",
    },
    "EnergyAustralia": {
        "color": colors.HexColor("#005BAB"),
        "accent": colors.HexColor("#95C11F"),
        "logo_text": "EnergyAustralia",
        "tagline": "Together. Better.",
        "states": ["NSW", "VIC", "QLD", "SA"],
        "abn": "99 086 410 327",
        "address": "EnergyAustralia Pty Ltd, Level 19, 2 Southbank Blvd, Southbank VIC 3006",
    },
    "RedEnergy": {
        "color": colors.HexColor("#E20020"),
        "accent": colors.HexColor("#000000"),
        "logo_text": "Red Energy",
        "tagline": "Good energy",
        "states": ["VIC", "NSW", "QLD", "SA"],
        "abn": "60 109 317 651",
        "address": "Red Energy Pty Ltd, GPO Box 4135, Melbourne VIC 3001",
    },
    "Alinta": {
        "color": colors.HexColor("#005C2F"),
        "accent": colors.HexColor("#FFC72C"),
        "logo_text": "Alinta",
        "tagline": "Energy for tomorrow",
        "states": ["WA", "SA", "VIC", "NSW"],
        "abn": "65 108 552 132",
        "address": "Alinta Energy, Level 14, 12-14 The Esplanade, Perth WA 6000",
    },
    "Synergy": {
        "color": colors.HexColor("#00A3E0"),
        "accent": colors.HexColor("#003B5C"),
        "logo_text": "synergy",
        "tagline": "WA's largest energy provider",
        "states": ["WA"],
        "abn": "57 110 308 221",
        "address": "Synergy, 228 Adelaide Terrace, Perth WA 6000",
    },
}

TARIFF_TYPES = [
    "single_rate",
    "time_of_use",
    "flexible_pricing",
    "demand",
    "controlled_load",
]

STATE_POSTCODES = {
    "NSW": ["2000", "2010", "2031", "2060", "2100", "2150", "2200", "2250", "2300", "2500"],
    "VIC": ["3000", "3056", "3101", "3121", "3141", "3181", "3205", "3300", "3500", "3800"],
    "QLD": ["4000", "4067", "4101", "4151", "4205", "4305", "4400", "4500", "4700", "4810"],
    "SA": ["5000", "5067", "5108", "5159", "5203", "5251", "5290", "5350", "5400", "5500"],
    "WA": ["6000", "6056", "6107", "6153", "6210", "6280", "6330", "6407", "6430", "6530"],
    "ACT": ["2600", "2606", "2612", "2615", "2617", "2620"],
    "TAS": ["7000", "7010", "7018", "7050", "7170", "7250", "7310", "7469"],
    "NT": ["0800", "0810", "0820", "0830"],
}

PLAN_NAMES = {
    "AGL": ["Essentials Single Rate", "Savings Weekender", "Solar Savers", "Business Essentials"],
    "Origin": ["Everyday", "Boost", "Go Variable", "Solar Boost", "Business Saver"],
    "EnergyAustralia": ["Total Plan Home", "Flexi Plan", "Total Plan Business", "Solar Plus"],
    "RedEnergy": ["Living Energy Saver", "Living Energy", "Qantas Red Saver", "Qantas Red Plus"],
    "Alinta": ["Fair Deal", "Home Deal", "Value Saver", "Business Deal"],
    "Synergy": ["Home Plan A1", "Home Plan A2", "Business Plan B1", "Time of Use"],
}

FUEL_TYPES = ["electricity", "gas"]

QUALITY_PROFILES = [
    "clean",          # Pristine PDF export
    "scanned_clean",  # Slight noise from scanner
    "scanned_warped", # Slight rotation, lower contrast
    "photo",          # Mobile photo of bill on table
    "fax",            # Low quality fax-style
]


# ---------------------------------------------------------------------------
# Data generation
# ---------------------------------------------------------------------------

def generate_nmi(state, fuel="electricity"):
    """Generate a realistic 10-11 digit NMI."""
    if fuel == "gas":
        # Gas NMIs use MIRN format
        mirn_prefix = random.choice(["4", "5", "6", "7"])
        return f"{mirn_prefix}{''.join(random.choices('0123456789', k=10))}"
    else:
        # Electricity NMI - 10 or 11 digits starting with state-specific prefix
        prefix_map = {
            "NSW": ["4", "7"],
            "VIC": ["6"],
            "QLD": ["3", "4"],
            "SA": ["8"],
            "WA": ["8", "9"],
            "ACT": ["7"],
            "TAS": ["6", "7"],
            "NT": ["3"],
        }
        prefix = random.choice(prefix_map.get(state, ["4"]))
        return f"{prefix}{''.join(random.choices('0123456789', k=10))}"


def generate_account_number():
    """Generate a retailer account number."""
    return f"{''.join(random.choices('0123456789', k=9))}"


def generate_bill_period():
    """Generate a bill period (30-90 days)."""
    days = random.choice([30, 31, 60, 61, 62, 90, 91])
    end_date = datetime(2025, 6, 30) - timedelta(days=random.randint(0, 365))
    start_date = end_date - timedelta(days=days)
    return start_date, end_date, days


def generate_consumption(days, fuel, season, business_type=None):
    """Generate realistic consumption in kWh or MJ."""
    # Seasonal adjustment
    seasonal_factor = {
        "summer": 1.4 if fuel == "electricity" else 0.6,
        "winter": 1.3 if fuel == "electricity" else 1.6,
        "spring": 1.0,
        "autumn": 1.0,
    }[season]

    if fuel == "electricity":
        if business_type:
            base_per_day = random.uniform(20, 200)  # SME range
        else:
            base_per_day = random.uniform(8, 30)    # residential
    else:  # gas
        if business_type:
            base_per_day = random.uniform(50, 500)
        else:
            base_per_day = random.uniform(20, 100)

    total = base_per_day * days * seasonal_factor
    return round(total, 2)


def generate_tariff_components(consumption, tariff_type, fuel, state):
    """Generate tariff breakdown."""
    if fuel == "electricity":
        if tariff_type == "single_rate":
            rate = round(random.uniform(0.25, 0.40), 4)
            usage_charge = round(consumption * rate, 2)
            daily_charge = round(random.uniform(0.85, 1.20), 2)
            supply_charge = round(daily_charge * random.randint(30, 92), 2)
        elif tariff_type == "time_of_use":
            peak_rate = round(random.uniform(0.40, 0.55), 4)
            shoulder_rate = round(random.uniform(0.25, 0.35), 4)
            offpeak_rate = round(random.uniform(0.15, 0.25), 4)
            peak_kwh = consumption * 0.4
            shoulder_kwh = consumption * 0.3
            offpeak_kwh = consumption * 0.3
            usage_charge = round(
                peak_kwh * peak_rate + shoulder_kwh * shoulder_rate + offpeak_kwh * offpeak_rate,
                2,
            )
            daily_charge = round(random.uniform(0.95, 1.30), 2)
            supply_charge = round(daily_charge * random.randint(30, 92), 2)
        elif tariff_type == "demand":
            flat_rate = round(random.uniform(0.20, 0.30), 4)
            demand_rate = round(random.uniform(15, 30), 2)
            peak_demand_kw = round(random.uniform(5, 50), 1)
            usage_charge = round(consumption * flat_rate, 2)
            demand_charge = round(peak_demand_kw * demand_rate * random.randint(1, 3), 2)
            daily_charge = round(random.uniform(1.20, 2.00), 2)
            supply_charge = round(daily_charge * random.randint(30, 92), 2)
            return {
                "flat_rate": flat_rate,
                "demand_rate": demand_rate,
                "peak_demand_kw": peak_demand_kw,
                "usage_charge": usage_charge,
                "demand_charge": demand_charge,
                "supply_charge": supply_charge,
            }
        else:  # flexible_pricing
            rate = round(random.uniform(0.28, 0.38), 4)
            usage_charge = round(consumption * rate, 2)
            daily_charge = round(random.uniform(0.90, 1.15), 2)
            supply_charge = round(daily_charge * random.randint(30, 92), 2)
    else:  # gas
        rate = round(random.uniform(0.025, 0.045), 4)
        usage_charge = round(consumption * rate, 2)
        daily_charge = round(random.uniform(0.40, 0.80), 2)
        supply_charge = round(daily_charge * random.randint(30, 92), 2)

    # Add discounts and credits
    discount = round(usage_charge * random.uniform(0, 0.15), 2)
    solar_credit = round(consumption * random.uniform(0, 0.05), 2) if random.random() < 0.3 else 0

    return {
        "usage_charge": usage_charge,
        "supply_charge": supply_charge,
        "discount": discount,
        "solar_credit": solar_credit,
    }


def generate_bill_data():
    """Generate complete bill data."""
    retailer_key = random.choice(list(RETAILERS.keys()))
    retailer = RETAILERS[retailer_key]
    state = random.choice(retailer["states"])
    postcode = random.choice(STATE_POSTCODES[state])
    fuel = random.choice(FUEL_TYPES)
    tariff_type = random.choice(TARIFF_TYPES) if fuel == "electricity" else "single_rate"
    business_type = random.choice(["cafe", "office", "retail", "warehouse"]) if random.random() < 0.4 else None

    start_date, end_date, days = generate_bill_period()
    consumption = generate_consumption(days, fuel, "summer" if start_date.month in [12,1,2] else "winter" if start_date.month in [6,7,8] else "spring", business_type)
    tariff = generate_tariff_components(consumption, tariff_type, fuel, state)

    # Calculate total (GST inclusive)
    subtotal = sum(v for k, v in tariff.items() if k != "solar_credit")
    subtotal -= tariff.get("solar_credit", 0)
    gst = round(subtotal * 0.10, 2)
    total = round(subtotal + gst, 2)

    return {
        "retailer": retailer_key,
        "retailer_data": retailer,
        "fuel": fuel,
        "state": state,
        "postcode": postcode,
        "nmi": generate_nmi(state, fuel),
        "account_number": generate_account_number(),
        "customer_name": Faker().name(),
        "supply_address": f"{random.randint(1, 999)} {random.choice(['George', 'Smith', 'Main', 'High', 'Park', 'Glen', 'Bay', 'King', 'Queen', 'Elizabeth'])} {random.choice(['St', 'Rd', 'Ave', 'Pl', 'Dr', 'Ct', 'Way'])}, {state} {postcode}",
        "plan_name": random.choice(PLAN_NAMES[retailer_key]),
        "tariff_type": tariff_type,
        "business_type": business_type,
        "billing_period": {
            "start": start_date.strftime("%d %b %Y"),
            "end": end_date.strftime("%d %b %Y"),
            "days": days,
        },
        "consumption": consumption,
        "tariff_breakdown": tariff,
        "subtotal": round(subtotal, 2),
        "gst": gst,
        "total": total,
        "due_date": (end_date + timedelta(days=random.randint(14, 28))).strftime("%d %b %Y"),
    }


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

def render_bill_pdf(bill_data, output_path):
    """Render a retailer-styled PDF bill."""
    filename = output_path
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    retailer = bill_data["retailer_data"]

    # Header
    c.setFillColor(retailer["color"])
    c.rect(0, height - 50*mm, width, 50*mm, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(20*mm, height - 30*mm, retailer["logo_text"])
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(20*mm, height - 38*mm, retailer["tagline"])

    # Bill title
    c.setFillColor(retailer["accent"])
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20*mm, height - 65*mm, f"{bill_data['fuel'].title()} Bill")

    # Account info box
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    y = height - 80*mm
    info_lines = [
        f"Account number: {bill_data['account_number']}",
        f"NMI/MIRN: {bill_data['nmi']}",
        f"Customer: {bill_data['customer_name']}",
        f"Supply address: {bill_data['supply_address']}",
        f"Plan: {bill_data['plan_name']}",
        f"Billing period: {bill_data['billing_period']['start']} to {bill_data['billing_period']['end']} ({bill_data['billing_period']['days']} days)",
        f"Due date: {bill_data['due_date']}",
    ]
    for line in info_lines:
        c.drawString(20*mm, y, line)
        y -= 6*mm

    # Total amount due - large prominent box
    c.setFillColor(retailer["accent"])
    c.rect(width - 80*mm, height - 100*mm, 65*mm, 25*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 10)
    c.drawString(width - 75*mm, height - 85*mm, "Total amount due")
    c.setFont("Helvetica-Bold", 22)
    c.drawString(width - 75*mm, height - 95*mm, f"${bill_data['total']:.2f}")

    # Consumption section
    y = height - 120*mm
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(20*mm, y, "Your usage this period")
    y -= 10*mm

    consumption_unit = "kWh" if bill_data["fuel"] == "electricity" else "MJ"
    c.setFont("Helvetica-Bold", 24)
    c.drawString(20*mm, y, f"{bill_data['consumption']:,.1f}")
    c.setFont("Helvetica", 11)
    c.drawString(85*mm, y, consumption_unit)
    y -= 15*mm

    # Tariff breakdown table
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20*mm, y, "Charges breakdown")
    y -= 6*mm

    c.setFont("Helvetica", 10)
    breakdown = bill_data["tariff_breakdown"]

    for key, value in breakdown.items():
        label = key.replace("_", " ").title()
        if key == "solar_credit" and value > 0:
            c.drawString(20*mm, y, f"{label}: -${value:.2f}")
            y -= 5*mm
        elif key == "discount" and value > 0:
            c.drawString(20*mm, y, f"{label}: -${value:.2f}")
            y -= 5*mm
        else:
            c.drawString(20*mm, y, f"{label}: ${value:.2f}")
            y -= 5*mm

    y -= 3*mm
    c.drawString(20*mm, y, f"GST (10%): ${bill_data['gst']:.2f}")
    y -= 8*mm

    # Footer
    c.setFillColor(colors.HexColor("#666666"))
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(20*mm, 25*mm, retailer["address"])
    c.drawString(20*mm, 20*mm, f"ABN: {retailer['abn']}")
    c.drawString(20*mm, 15*mm, f"Generated for testing purposes only - Not a real bill")

    c.showPage()
    c.save()


def render_gas_bill_pdf(bill_data, output_path):
    """Render a gas-specific bill (slightly different layout)."""
    filename = output_path
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    retailer = bill_data["retailer_data"]

    # Different header style for gas
    c.setFillColor(retailer["color"])
    c.rect(0, height - 35*mm, width, 35*mm, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(20*mm, height - 22*mm, retailer["logo_text"])
    c.setFont("Helvetica", 10)
    c.drawString(width - 80*mm, height - 22*mm, "Gas Supply Account")

    # Account details
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, height - 50*mm, "Account Summary")

    c.setFont("Helvetica", 10)
    y = height - 60*mm
    details = [
        f"Account: {bill_data['account_number']}",
        f"MIRN: {bill_data['nmi']}",
        f"Customer: {bill_data['customer_name']}",
        f"Address: {bill_data['supply_address']}",
        f"Plan: {bill_data['plan_name']}",
        f"Period: {bill_data['billing_period']['start']} - {bill_data['billing_period']['end']}",
    ]
    for line in details:
        c.drawString(20*mm, y, line)
        y -= 5*mm

    # Charges
    y -= 5*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, y, "Charges")
    y -= 7*mm

    c.setFont("Helvetica", 10)
    c.drawString(20*mm, y, f"Gas usage ({bill_data['consumption']:.0f} MJ)")
    c.drawString(width - 60*mm, y, f"${bill_data['tariff_breakdown']['usage_charge']:.2f}")
    y -= 5*mm

    c.drawString(20*mm, y, f"Supply charge ({bill_data['billing_period']['days']} days)")
    c.drawString(width - 60*mm, y, f"${bill_data['tariff_breakdown']['supply_charge']:.2f}")
    y -= 5*mm

    if bill_data['tariff_breakdown'].get('discount', 0) > 0:
        c.drawString(20*mm, y, "Pay on time discount")
        c.drawString(width - 60*mm, y, f"-${bill_data['tariff_breakdown']['discount']:.2f}")
        y -= 5*mm

    y -= 3*mm
    c.drawString(20*mm, y, f"GST")
    c.drawString(width - 60*mm, y, f"${bill_data['gst']:.2f}")
    y -= 8*mm

    # Total due
    c.setFillColor(retailer["accent"])
    c.rect(width - 85*mm, y - 12*mm, 70*mm, 15*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 80*mm, y - 5*mm, "Total due")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(width - 80*mm, y - 11*mm, f"${bill_data['total']:.2f}")

    # Footer
    c.setFillColor(colors.HexColor("#666666"))
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(20*mm, 15*mm, f"{retailer['address']} | ABN: {retailer['abn']}")

    c.showPage()
    c.save()


# ---------------------------------------------------------------------------
# Quality degradation (for OCR stress testing)
# ---------------------------------------------------------------------------

def degrade_pdf_to_image(pdf_path, output_path, quality):
    """Convert PDF to image with quality degradation."""
    # Convert PDF to image (first page)
    from pdf2image import convert_from_path

    images = convert_from_path(pdf_path, dpi=200)
    if not images:
        return False

    img = images[0]

    if quality == "scanned_clean":
        # Slight noise
        import numpy as np
        arr = np.array(img)
        noise = np.random.randint(-15, 15, arr.shape, dtype=np.int16)
        arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)

    elif quality == "scanned_warped":
        # Slight rotation and lower contrast
        img = img.rotate(random.uniform(-2, 2), fillcolor=(255, 255, 255))
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(0.8)
        # Add slight blur
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    elif quality == "photo":
        # Simulate mobile photo with perspective warp and lighting
        img = img.rotate(random.uniform(-3, 3), fillcolor=(200, 200, 200))
        # Darken edges
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        # Add some shadow
        draw.rectangle([0, 0, img.width, 100], fill=(50, 50, 50))
        # Slight blur
        img = img.filter(ImageFilter.GaussianBlur(radius=0.3))

    elif quality == "fax":
        # Low resolution, high contrast
        img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
        img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        img = img.convert("L")  # Grayscale

    img.save(output_path, "JPEG", quality=85 if quality != "fax" else 60)
    return True


# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------

def generate_bill_set(output_dir, count=10):
    """Generate a set of bills with variations."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    bills_dir = output_dir / "bills"
    bills_dir.mkdir(exist_ok=True)

    metadata = []

    for i in range(count):
        bill_data = generate_bill_data()
        quality = random.choice(QUALITY_PROFILES)

        # Generate filename
        retailer_safe = bill_data["retailer"].replace(" ", "_")
        fuel_safe = bill_data["fuel"]
        state_safe = bill_data["state"]

        # Save PDF
        pdf_filename = f"{retailer_safe}_{fuel_safe}_{state_safe}_{i:03d}_{quality}.pdf"
        pdf_path = bills_dir / pdf_filename

        # Render PDF
        if bill_data["fuel"] == "electricity":
            render_bill_pdf(bill_data, str(pdf_path))
        else:
            render_gas_bill_pdf(bill_data, str(pdf_path))

        # Degrade to image if needed
        if quality != "clean":
            try:
                img_filename = pdf_filename.replace(".pdf", ".jpg")
                img_path = bills_dir / img_filename
                if degrade_pdf_to_image(str(pdf_path), str(img_path), quality):
                    # Remove PDF, keep only image for OCR testing
                    os.remove(pdf_path)
                    final_path = str(img_path)
                else:
                    final_path = str(pdf_path)
            except ImportError:
                # pdf2image not available, keep PDF
                final_path = str(pdf_path)
        else:
            final_path = str(pdf_path)

        # Save metadata
        metadata.append({
            "file": os.path.basename(final_path),
            "quality": quality,
            "ground_truth": bill_data,
        })

    # Write metadata
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    print(f"Generated {count} bills in {output_dir}")
    print(f"Metadata saved to {metadata_path}")
    print(f"\nSample distribution:")
    from collections import Counter
    print(f"  Retailers: {Counter([m['ground_truth']['retailer'] for m in metadata])}")
    print(f"  Fuels: {Counter([m['ground_truth']['fuel'] for m in metadata])}")
    print(f"  Quality: {Counter([m['quality'] for m in metadata])}")
    print(f"  States: {Counter([m['ground_truth']['state'] for m in metadata])}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic Australian energy bills for OCR testing")
    parser.add_argument("--output", default="./synthetic_bills", help="Output directory")
    parser.add_argument("--count", type=int, default=50, help="Number of bills to generate")

    args, unknown = parser.parse_known_args()
    generate_bill_set(args.output, args.count)
