from datetime import datetime
from dateutil.relativedelta import relativedelta

FACE_VALUE = 100
COUPON_TAX_RATE = 0.45

# --- Inputs ---
expiry_str = input("Expiration date (dd/mm/yyyy): ")
coupon_rate = float(input("Coupon rate: "))
price = float(input("Bond price: "))
frequency = int(input("Coupon frequency (1=annual, 2=semiannual, 4=quarterly): "))

maturity = datetime.strptime(expiry_str, "%d/%m/%Y")
today = datetime.today()

# --- Coupon calculations ---
gross_coupon_annual = FACE_VALUE * coupon_rate/100
gross_coupon_per_period = gross_coupon_annual / frequency
net_coupon = gross_coupon_per_period * (1 - COUPON_TAX_RATE)

# --- Count remaining payments ---
months = int(12 / frequency)
payment_date = today
total_cashflows = 0

while True:
    payment_date = payment_date + relativedelta(months=months)
    
    if payment_date >= maturity:
        break
        
    total_cashflows += net_coupon

# final payment
total_cashflows += net_coupon + FACE_VALUE

# --- Years until maturity ---
T = (maturity - today).days / 365.25

# --- Equivalent annual rate ---
r = (total_cashflows / price) ** (1 / T) - 1

print("\nResults")
print("Total cash received:", round(total_cashflows,2))
print("Equivalent annual interest rate:", round(r*100,3), "%")