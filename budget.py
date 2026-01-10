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


def get_user_input(prompt, type_=str, allow_back=True):
    """Generic input with type checking and 'back' option"""
    while True:
        user_input = input(prompt).strip()
        if allow_back and user_input.lower() == "b":
            return "BACK"
        try:
            return type_(user_input)
        except ValueError:
            print(f"Invalid input. Expected a {type_.__name__}.\n")


def add_expense(expenses, categories):
    while True:
        print("\nChoose a category (or press 'B' to go back):")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")

        category_input = get_user_input("Category number: ", int)
        if category_input == "BACK":
            return

        if 1 <= category_input <= len(categories):
            category = categories[category_input - 1]
        else:
            print("Invalid category number. Try again.")
            continue

        amount = get_user_input("Amount: £", float)
        if amount == "BACK":
            return

        description = input("Description (free text, press enter to skip, B to go back): ").strip()
        if description.lower() == "b":
            return

        expense = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "category": category,
            "amount": amount,
            "description": description,
        }

        expenses.append(expense)
        save_expenses(expenses)
        log_history(f"Added expense: £{amount:.2f} | {category} | {description}")

        print("Expense added successfully!\n")

        # Ask if user wants to add another
        cont = input("Add another expense? (y/n): ").strip().lower()
        if cont != "y":
            break


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
    expenses = load_expenses()

    while True:
        print()
        print("=== Budget App ===")
        print("1. Add expense")
        print("2. View summary")
        print("3. View expense history")
        print("4. Exit")

        choice = get_user_input("\nChoose an option: ", int, allow_back=False)

        if choice == 1:
            add_expense(expenses, categories)
        elif choice == 2:
            show_summary(expenses, categories)
        elif choice == 3:
            show_history(expenses)
        elif choice == 4:
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please select 1-4.")


if __name__ == "__main__":
    main()
