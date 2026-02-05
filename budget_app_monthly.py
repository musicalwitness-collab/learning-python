import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
from pathlib import Path

APP_DIR = Path.home() / "BudgetApp"
APP_DIR.mkdir(exist_ok=True)
DATA_FILE = APP_DIR / "budget_data.csv"


class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Budget Tracker (Monthly View)")
        self.resizable(False, False)

        self.transactions = []  # list of dicts

        # --- Top: Income entry ---
        top = ttk.Frame(self, padding=12)
        top.grid(row=0, column=0, sticky="ew")

        ttk.Label(top, text="Income amount:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.income_entry = ttk.Entry(top, width=18)
        self.income_entry.grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(top, text="Add Income", command=self.add_income).grid(row=0, column=2, padx=6, pady=6)

        # --- Monthly filter row ---
        ttk.Label(top, text="View month:").grid(row=0, column=3, sticky="e", padx=6, pady=6)
        self.month_var = tk.StringVar(value="All")
        self.month_menu = ttk.Combobox(top, textvariable=self.month_var, values=["All"], width=10, state="readonly")
        self.month_menu.grid(row=0, column=4, padx=6, pady=6)
        self.month_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        ttk.Button(top, text="Show All", command=self.show_all).grid(row=0, column=5, padx=6, pady=6)

        # --- Middle: Expense entry ---
        mid = ttk.Frame(self, padding=12)
        mid.grid(row=1, column=0, sticky="ew")

        ttk.Label(mid, text="Expense amount:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.expense_entry = ttk.Entry(mid, width=18)
        self.expense_entry.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(mid, text="Category:").grid(row=0, column=2, sticky="e", padx=6, pady=6)
        self.category = tk.StringVar(value="Groceries")
        self.category_menu = ttk.Combobox(
            mid,
            textvariable=self.category,
            values=["Groceries", "Dining", "Gas", "Bills", "Shopping", "Health", "Entertainment", "Other"],
            width=16,
            state="readonly",
        )
        self.category_menu.grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(mid, text="Note:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.note_entry = ttk.Entry(mid, width=48)
        self.note_entry.grid(row=1, column=1, columnspan=3, padx=6, pady=6, sticky="w")

        ttk.Button(mid, text="Add Expense", command=self.add_expense).grid(row=0, column=4, rowspan=2, padx=6, pady=6)

        # --- Table ---
        table_frame = ttk.Frame(self, padding=12)
        table_frame.grid(row=2, column=0, sticky="ew")

        cols = ("date", "type", "amount", "category", "note")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.heading("date", text="Date")
        self.tree.heading("type", text="Type")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("category", text="Category")
        self.tree.heading("note", text="Note")

        self.tree.column("date", width=110, anchor="w")
        self.tree.column("type", width=70, anchor="w")
        self.tree.column("amount", width=90, anchor="e")
        self.tree.column("category", width=110, anchor="w")
        self.tree.column("note", width=260, anchor="w")

        # --- Bottom: Totals + buttons ---
        bottom = ttk.Frame(self, padding=12)
        bottom.grid(row=3, column=0, sticky="ew")

        self.income_total_var = tk.StringVar(value="0.00")
        self.expense_total_var = tk.StringVar(value="0.00")
        self.balance_var = tk.StringVar(value="0.00")

        ttk.Label(bottom, text="Income:").grid(row=0, column=0, padx=6, pady=4, sticky="e")
        ttk.Label(bottom, textvariable=self.income_total_var, width=10).grid(row=0, column=1, padx=6, pady=4, sticky="w")

        ttk.Label(bottom, text="Expenses:").grid(row=0, column=2, padx=6, pady=4, sticky="e")
        ttk.Label(bottom, textvariable=self.expense_total_var, width=10).grid(row=0, column=3, padx=6, pady=4, sticky="w")

        ttk.Label(bottom, text="Balance:").grid(row=0, column=4, padx=6, pady=4, sticky="e")
        ttk.Label(bottom, textvariable=self.balance_var, width=10).grid(row=0, column=5, padx=6, pady=4, sticky="w")

        ttk.Button(bottom, text="Delete Selected", command=self.delete_selected).grid(row=0, column=6, padx=10, pady=4)
        ttk.Button(bottom, text="Save", command=self.save).grid(row=0, column=7, padx=6, pady=4)
        ttk.Button(bottom, text="Load", command=self.load).grid(row=0, column=8, padx=6, pady=4)

        self.bind("<Return>", lambda e: self.add_expense())  # Enter adds expense

        # Auto-load
        if DATA_FILE.exists():
            self.load()
        else:
            # default month list to current month even if no file yet
            self.rebuild_month_list()
            self.refresh_table()

    # ---------- Helpers ----------
    def _parse_amount(self, text: str) -> float:
        t = text.strip().replace("$", "")
        if not t:
            raise ValueError("Empty amount")
        return float(t)

    def month_key(self, date_str: str) -> str:
        # expecting YYYY-MM-DD
        return date_str[:7]  # YYYY-MM

    def current_filter(self) -> str:
        return self.month_var.get()

    def filtered_transactions(self):
        m = self.current_filter()
        if m == "All":
            return list(self.transactions)
        return [tx for tx in self.transactions if self.month_key(tx["date"]) == m]

    def rebuild_month_list(self):
        months = sorted({self.month_key(tx["date"]) for tx in self.transactions}, reverse=True)
        values = ["All"] + months
        self.month_menu["values"] = values
        # If current selection vanished, reset
        if self.month_var.get() not in values:
            self.month_var.set("All")

    def refresh_table(self):
        # clear table
        for row in self.tree.get_children():
            self.tree.delete(row)

        # insert filtered rows
        for tx in self.filtered_transactions():
            self.tree.insert(
                "",
                tk.END,
                values=(tx["date"], tx["type"], f'{tx["amount"]:.2f}', tx["category"], tx["note"]),
            )

        self.update_totals()

    def show_all(self):
        self.month_var.set("All")
        self.refresh_table()

    # ---------- Actions ----------
    def add_income(self):
        try:
            amount = self._parse_amount(self.income_entry.get())
            if amount <= 0:
                raise ValueError("Income must be > 0")
            tx = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": "Income",
                "amount": amount,
                "category": "Income",
                "note": "",
            }
            self.transactions.append(tx)
            self.income_entry.delete(0, tk.END)
            self.income_entry.focus_set()

            self.rebuild_month_list()
            # keep current filter; refresh view
            self.refresh_table()
        except ValueError:
            messagebox.showerror("Invalid income", "Please enter a valid income amount (example: 1500).")

    def add_expense(self):
        try:
            amount = self._parse_amount(self.expense_entry.get())
            if amount <= 0:
                raise ValueError("Expense must be > 0")
            tx = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "type": "Expense",
                "amount": amount,
                "category": self.category.get(),
                "note": self.note_entry.get().strip(),
            }
            self.transactions.append(tx)
            self.expense_entry.delete(0, tk.END)
            self.note_entry.delete(0, tk.END)
            self.expense_entry.focus_set()

            self.rebuild_month_list()
            self.refresh_table()
        except ValueError:
            messagebox.showerror("Invalid expense", "Please enter a valid expense amount (example: 23.45).")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return

        # Build a set of row-values to remove
        to_remove = set()
        for item_id in selected:
            vals = self.tree.item(item_id, "values")
            to_remove.add(vals)

        # Remove from the master list (match on displayed string values)
        new_list = []
        for tx in self.transactions:
            row_vals = (tx["date"], tx["type"], f'{tx["amount"]:.2f}', tx["category"], tx["note"])
            if row_vals not in to_remove:
                new_list.append(tx)
        self.transactions = new_list

        self.rebuild_month_list()
        self.refresh_table()

    def update_totals(self):
        visible = self.filtered_transactions()
        income = sum(tx["amount"] for tx in visible if tx["type"] == "Income")
        expenses = sum(tx["amount"] for tx in visible if tx["type"] == "Expense")
        balance = income - expenses
        self.income_total_var.set(f"{income:.2f}")
        self.expense_total_var.set(f"{expenses:.2f}")
        self.balance_var.set(f"{balance:.2f}")

    def save(self):
        try:
            with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "type", "amount", "category", "note"])
                writer.writeheader()
                for tx in self.transactions:
                    writer.writerow(tx)
            messagebox.showinfo("Saved", f"Saved to:\n{DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    def load(self):
        try:
            self.transactions.clear()

            if not DATA_FILE.exists():
                messagebox.showinfo("No data", "No saved data found yet.")
                self.rebuild_month_list()
                self.refresh_table()
                return

            with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    tx = {
                        "date": r["date"],
                        "type": r["type"],
                        "amount": float(r["amount"]),
                        "category": r["category"],
                        "note": r["note"],
                    }
                    self.transactions.append(tx)

            self.rebuild_month_list()
            # default to latest month (optional). Comment out if you prefer "All".
            months = [m for m in self.month_menu["values"] if m != "All"]
            if months:
                self.month_var.set(months[0])  # latest month
            else:
                self.month_var.set("All")

            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Load failed", str(e))


if __name__ == "__main__":
    app = BudgetApp()
    app.mainloop()
