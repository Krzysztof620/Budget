import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

CONFIG_FILE = Path("config.json")
EXPENSES_FILE = Path("expenses.json")
HISTORY_FILE = Path("history.log")


def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError("config.json not found")
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def load_expenses():
    if EXPENSES_FILE.exists():
        with open(EXPENSES_FILE, "r") as f:
            return json.load(f)
    return []


def save_expenses(expenses):
    with open(EXPENSES_FILE, "w") as f:
        json.dump(expenses, f, indent=2)


def log_history(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HISTORY_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def add_expense(expenses, categories):
    print("\nChoose a category:")
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat}")

    category = categories[int(input("Category number: ")) - 1]
    amount = float(input("Amount: "))
    description = input("Description (free text): ")

    expense = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "category": category,
        "amount": amount,
        "description": description,
    }

    expenses.append(expense)
    save_expenses(expenses)
    log_history(f"Added expense: £{amount:.2f} | {category} | {description}")

    print("Expense added.\n")


def show_summary(expenses, categories):
    summary = {cat: 0 for cat in categories}
    for exp in expenses:
        summary[exp["category"]] += exp["amount"]

    print("\nExpense Summary:")
    for cat, total in summary.items():
        print(f"\t{cat}: £{total:.2f}")
    print()


def show_history(expenses):
    print("\nExpense History:")
    for exp in expenses:
        print(
            f'{exp["date"]} | {exp["category"]} | '
            f'£{exp["amount"]:.2f} | {exp["description"]}'
        )
    print()


def main():
    config = load_config()
    categories = config["categories"]
    monthly_groups = config['monthly_groups']
    monthly_derived = config['monthly_derived']
    expenses = load_expenses()

    while True:
        print("Budget App")
        print("1. Add expense")
        print("2. View summary")
        print("3. View expense history")
        print("4. Exit")
        
        choice = input("Choose an option: ")

        if choice == "1":
            add_expense(expenses, categories)
        elif choice == "2":
            show_summary(expenses, categories)
        elif choice == "3":
            show_history(expenses)
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()
