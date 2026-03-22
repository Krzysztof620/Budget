import pandas as pd
from datetime import datetime

# To download the report about gilts, go here: https://www.dmo.gov.uk/data/pdfdatareport?reportCode=D1A

# -----------------------------
# Helper functions
# -----------------------------

def parse_date(date_str):
    """Parse a date string like '31 Jan 2028'"""
    return datetime.strptime(date_str.strip(), "%d %b %Y")

def accrued_interest(clean_price, coupon_rate, settlement_date, last_coupon_date, face_value=100):
    """
    Calculate accrued interest to add to clean price.
    """
    days_between_coupons = (settlement_date - last_coupon_date).days
    coupon_period_days = 182.5  # approx 6 months
    semi_coupon = coupon_rate / 2 * face_value
    return semi_coupon * (days_between_coupons / coupon_period_days)

def generate_coupon_dates(first_issue, redemption, dividend_dates):
    """
    Generate all coupon dates between first issue and redemption.
    dividend_dates: string like '22 Jan/Jul'
    """
    start_year = first_issue.year
    end_year = redemption.year
    schedule = []

    day_months = []
    for dm in dividend_dates.split('/'):
        day, mon = dm.split()
        day_months.append((int(day), mon))

    for y in range(start_year, end_year + 1):
        for day, mon in day_months:
            try:
                dt = datetime.strptime(f"{day} {mon} {y}", "%d %b %Y")
            except:
                continue
            if dt > first_issue and dt <= redemption:
                schedule.append(dt)
    return sorted(schedule)

def simplified_yield(dirty_price, coupons, face_value, years_to_maturity):
    """
    Compute after-tax annual yield assuming all cashflows are at maturity
    """
    total_inflows = sum(coupons) + face_value
    r = (total_inflows / dirty_price) ** (1 / years_to_maturity) - 1
    return r

# -----------------------------
# Example input tables
# -----------------------------

# Market table (clean prices)
market_data = pd.DataFrame({
    "Issuer": ["Treasury 0.125% 31/01/2028"],
    "Coupon (%)": [0.125],
    "Maturity": ["31 Jan 2028"],
    "Price": [92.490]  # clean price
})

# Gilt details table
details_data = pd.DataFrame({
    "Conventional Gilts": ["Treasury 0.125% 31/01/2028"],
    "ISIN Code": ["GB00BMBL1G81"],
    "Redemption Date": ["31 Jan 2028"],
    "First Issue Date": ["22 Jan 2023"],
    "Dividend Dates": ["22 Jan/Jul"],
    "Ex-dividend Date": ["22 Jan 2028"],
    "Amount in Issue (£ million nominal)": ["1000"]
})

# Settlement date
settlement = datetime(2025, 8, 31)

# -----------------------------
# Compute simplified after-tax yield for each gilt
# -----------------------------

results = []

for _, row in market_data.iterrows():
    clean_price = row["Price"]
    coupon_rate = row["Coupon (%)"]
    maturity = parse_date(row["Maturity"])

    # Match gilt details
    details = details_data[details_data["Conventional Gilts"] == row["Issuer"]].iloc[0]
    first_issue = parse_date(details["First Issue Date"])
    dividend_dates = details["Dividend Dates"]

    # Coupon schedule
    coupon_schedule = generate_coupon_dates(first_issue, maturity, dividend_dates)
    last_coupon = max([d for d in coupon_schedule if d <= settlement])

    # Dirty price = clean + accrued interest
    dirty_price = clean_price + accrued_interest(clean_price, coupon_rate, settlement, last_coupon)

    # Number of semi-annual coupons remaining (after settlement)
    remaining_coupons = [c for c in coupon_schedule if c > settlement]
    semi_coupon_value = coupon_rate / 2 * 100  # per £100 face
    coupons_after_tax = [semi_coupon_value * (1 - 0.45) for _ in remaining_coupons]

    # Fractional years to maturity
    years_to_maturity = (maturity - settlement).days / 365

    # Simplified annual yield
    r = simplified_yield(dirty_price, coupons_after_tax, 100, years_to_maturity)

    results.append({
        "Gilt": row["Issuer"],
        "Dirty Price": round(dirty_price, 3),
        "After-tax annual yield": round(r * 100, 4)
    })

# -----------------------------
# Show results
# -----------------------------
results_df = pd.DataFrame(results)
print(results_df)