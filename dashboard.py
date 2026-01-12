import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ------------------------
# Files
# ------------------------
CONFIG_FILE = Path("config.json")
EXPENSES_FILE = Path("expenses.json")

# ------------------------
# Loaders
# ------------------------
def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_expenses():
    if EXPENSES_FILE.exists():
        with open(EXPENSES_FILE, "r") as f:
            return json.load(f)
    return []

# ------------------------
# Monthly summary logic
# ------------------------
def monthly_summary(expenses, categories, monthly_groups, monthly_derived):
    monthly = defaultdict(lambda: defaultdict(float))

    for exp in expenses:
        month = datetime.strptime(exp["date"], "%Y-%m-%d").strftime("%Y-%m")
        monthly[month][exp["category"]] += exp["amount"]

    results = {}

    for month, cats in monthly.items():
        result = {}

        # base categories
        for c in categories:
            result[c] = cats.get(c, 0)

        # grouped categories
        for group, members in monthly_groups.items():
            result[group] = sum(result[m] for m in members)

        # derived metrics
        for name, spec in monthly_derived.items():
            result[name] = eval(spec["formula"], {}, result)

        results[month] = result

    return results

# ------------------------
# App
# ------------------------
st.set_page_config(page_title="Budget App", layout="wide")
st.title("💰 Budget Dashboard")

config = load_config()
expenses = load_expenses()

categories = config["categories"]
monthly_groups = config["monthly_groups"]
monthly_derived = config["monthly_derived"]

if not expenses:
    st.warning("No expenses found.")
    st.stop()

# ------------------------
# Monthly summary
# ------------------------
st.header("📆 Monthly Summary")

summaries = monthly_summary(expenses, categories, monthly_groups, monthly_derived)
summary_df = pd.DataFrame.from_dict(summaries, orient="index")
summary_df.index.name = "Month"

# Ensure Flights, Special, Rent columns exist even if 0
for cat in ["Flights", "Special", "Rent"]:
    if cat not in summary_df.columns:
        summary_df[cat] = 0

# Decide the display order
display_cols = list(monthly_groups.keys()) + list(monthly_derived.keys()) + ["Special", "Flights", "Rent"]
display_cols = [c for c in display_cols if c not in ["Full spend", "Purchases + Utilities"]] + ["Full spend"]

print(display_cols)

st.dataframe(summary_df[display_cols].sort_index(), use_container_width=True)

# ------------------------
# DataFrame prep
# ------------------------
df = pd.DataFrame(expenses)
df["date"] = pd.to_datetime(df["date"]).dt.date

# ------------------------
# Expense Records
# ------------------------
st.header("📄 Expense Records")

records_df = df[["date", "category", "amount", "description"]] \
    .sort_values("date", ascending=False)

st.dataframe(records_df, use_container_width=True, hide_index=True)

# ------------------------
# Daily category spend
# ------------------------
st.header("📈 Cumulative Daily Spend by Category")

DEFAULT_DAILY_CATEGORIES = [
    "Commuting",
    "Groceries",
    "Food out",
    "Discretionary",
]

selected_categories = st.multiselect(
    "Select categories",
    categories,
    default=[c for c in DEFAULT_DAILY_CATEGORIES if c in categories],
)

# Ensure date is datetime and sorted
df["date"] = pd.to_datetime(df["date"])

daily_df = (
    df[df["category"].isin(selected_categories)]
    .groupby(["date", "category"], as_index=False)["amount"]
    .sum()
    .pivot(index="date", columns="category", values="amount")
    .fillna(0)
    .sort_index()
)

# Cumulative spend up to and including each date
cumulative_daily_df = daily_df.cumsum()

st.line_chart(cumulative_daily_df)


# ------------------------
# Category share by month (%)
# ------------------------
st.header("📊 Category Share by Month")

df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)

selected_month = st.selectbox(
    "Select month",
    sorted(df["month"].unique())
)

EXCLUDED_CATEGORIES = ["Rent"] 

month_df = (
    df[
        (df["month"] == selected_month)
        & (~df["category"].isin(EXCLUDED_CATEGORIES))
    ]
    .groupby("category")["amount"]
    .sum()
)

share_df = (month_df / month_df.sum() * 100).sort_values(ascending=False).round(1)

st.bar_chart(share_df)
