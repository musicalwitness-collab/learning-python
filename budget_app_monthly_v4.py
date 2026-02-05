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

        ttk.Label(top, text="Date (MM-DD-YYYY):").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.date_entry = ttk.Entry(top, width=10)
        self.date_entry.grid(row=0, column=1, padx=6, pady=6)
        self.date_entry.insert(0, datetime.now().strftime("%m-%d-%Y"))

        ttk.Label(top, text="Income amount:").grid(row=0, column=2, sticky="e", padx=6, pady=6)
        self.income_entry = ttk.Entry(top, width=10)
        self.income_entry.grid(row=0, column=3, padx=6, pady=6) 
        ttk.Button(top, text="Add Income", command=self.add_income).grid(row=0, column=4, padx=6, pady=6)

        

        # --- Monthly filter row ---
        ttk.Label(top, text="View month:").grid(row=0, column=5, sticky="e", padx=6, pady=6)
        self.month_var = tk.StringVar(value="All")
        self.month_menu = ttk.Combobox(top, textvariable=self.month_var, values=["All"], width=10, state="readonly")
        self.month_menu.grid(row=0, column=6, padx=6, pady=6)
        self.month_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        ttk.Button(top, text="◀ Prev", command=self.prev_month).grid(row=0, column=7, padx=4, pady=6)
        ttk.Button(top, text="Next ▶", command=self.next_month).grid(row=0, column=8, padx=4, pady=6)
        ttk.Button(top, text="Show All", command=self.show_all).grid(row=0, column=9, padx=6, pady=6)


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

        ttk.Button(bottom, text="Edit Selected", command=self.edit_selected).grid(row=0, column=6, padx=6, pady=4)
        ttk.Button(bottom, text="Delete Selected", command=self.delete_selected).grid(row=0, column=7, padx=6, pady=4)
        ttk.Button(bottom, text="Save", command=self.save).grid(row=0, column=8, padx=6, pady=4)
        ttk.Button(bottom, text="Load", command=self.load).grid(row=0, column=9, padx=6, pady=4)


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
        # expecting MM-DD-YYYY
        return date_str[:7]  # MM-YYYY

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

        # insert filtered rows with stable IDs (index from master list)
        current_month = self.month_var.get()

        for tx_index, tx in enumerate(self.transactions):
            if current_month != "All" and self.month_key(tx["date"]) != current_month:
                continue

            self.tree.insert(
                "",
                tk.END,
                iid=str(tx_index),
                values=(tx["date"], tx["type"], f'{tx["amount"]:.2f}', tx["category"], tx["note"]),
            )

        self.update_totals()


    def show_all(self):
        self.month_var.set("All")
        self.refresh_table()
    
    def _month_values_no_all(self):
        """Return the month list (MM-YYYY) newest -> oldest."""
        vals = list(self.month_menu["values"])
        return [v for v in vals if v != "All"]

    def prev_month(self):
        months = self._month_values_no_all()
        if not months:
             return

        current = self.month_var.get()
        # If on All, jump to newest month
        if current == "All":
            self.month_var.set(months[0])
            self.refresh_table()
            return
        
        try:
            i = months.index(current)
        except ValueError:
            self.month_var.set(months[0])
            self.refresh_table()
            return

        # months is newest->oldest, so "prev" means go OLDER => i+1
        if i + 1 < len(months):
            self.month_var.set(months[i + 1])
            self.refresh_table()

    def next_month(self):
        months = self._month_values_no_all()
        if not months:
            return

        current = self.month_var.get()
        # If on All, jump to newest month
        if current == "All":
            self.month_var.set(months[0])
            self.refresh_table()
            return
        try:
            i = months.index(current)
        except ValueError:
            self.month_var.set(months[0])
            self.refresh_table()
            return

        # months is newest->oldest, so "next" means go NEWER => i-1
        if i - 1 >= 0:
            self.month_var.set(months[i - 1])
            self.refresh_table()

    def _parse_date(self, text: str) -> str:
        t = text.strip()
        # Validates format and real date
        datetime.strptime(t, "%m-%d-%Y")
        return t
    
    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Edit", "Select a row to edit first.")
            return

        tx_index = int(selected[0])  # iid we set in refresh_table()
        tx = self.transactions[tx_index]

        win = tk.Toplevel(self)
        win.title("Edit Transaction")
        win.resizable(False, False)

        # Fields
        ttk.Label(win, text="Date (MM-DD-YYYY):").grid(row=0, column=0, padx=8, pady=6, sticky="e")
        date_e = ttk.Entry(win, width=14)
        date_e.grid(row=0, column=1, padx=8, pady=6)
        date_e.insert(0, tx["date"])

        ttk.Label(win, text="Type:").grid(row=1, column=0, padx=8, pady=6, sticky="e")
        type_var = tk.StringVar(value=tx["type"])
        type_menu = ttk.Combobox(win, textvariable=type_var, values=["Income", "Expense"], state="readonly", width=12)
        type_menu.grid(row=1, column=1, padx=8, pady=6, sticky="w")

        ttk.Label(win, text="Amount:").grid(row=2, column=0, padx=8, pady=6, sticky="e")
        amt_e = ttk.Entry(win, width=14)
        amt_e.grid(row=2, column=1, padx=8, pady=6)
        amt_e.insert(0, str(tx["amount"]))

        ttk.Label(win, text="Category:").grid(row=3, column=0, padx=8, pady=6, sticky="e")
        cat_var = tk.StringVar(value=tx["category"])
        cat_menu = ttk.Combobox(
             win,
            textvariable=cat_var,
            values=["Groceries", "Dining", "Gas", "Bills", "Shopping", "Health", "Entertainment", "Other", "Income"],
            state="readonly",
            width=18,
        )
        cat_menu.grid(row=3, column=1, padx=8, pady=6, sticky="w")

        ttk.Label(win, text="Note:").grid(row=4, column=0, padx=8, pady=6, sticky="e")
        note_e = ttk.Entry(win, width=28)
        note_e.grid(row=4, column=1, padx=8, pady=6, sticky="w")
        note_e.insert(0, tx["note"])

        def save_changes():
            try:
                new_date = self._parse_date(date_e.get())
                new_type = type_var.get()
                new_amount = self._parse_amount(amt_e.get())
                if new_amount <= 0:
                    raise ValueError("Amount must be > 0")
                new_cat = cat_var.get()
                if new_type == "Income":
                    new_cat = "Income"  # keep consistent
                new_note = note_e.get().strip()

                self.transactions[tx_index] = {
                    "date": new_date,
                    "type": new_type,
                    "amount": float(new_amount),
                    "category": new_cat,
                    "note": new_note,
                }

                self.rebuild_month_list()
                self.refresh_table()
                win.destroy()
            except Exception:
                messagebox.showerror("Invalid edit", "Check the date (YYYY-MM-DD) and amount.")

        btns = ttk.Frame(win)
        btns.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Save", command=save_changes).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Cancel", command=win.destroy).grid(row=0, column=1, padx=6)
        
    # ---------- Actions ----------
    def add_income(self):
        try:
            date_str = self._parse_date(self.date_entry.get())
            amount = self._parse_amount(self.income_entry.get())
            if amount <= 0:
                raise ValueError("Income must be > 0")
            tx = {
            "date": date_str,
            "type": "Income",
            "amount": amount,
            "category": "Income",
            "note": "",
            }
            self.transactions.append(tx)

            self.income_entry.delete(0, tk.END)
            self.income_entry.focus_set()

            self.rebuild_month_list()
            self.refresh_table()
        except Exception:
            messagebox.showerror("Invalid entry", "Use date format YYYY-MM-DD and a valid income amount (example: 1500).")

    def add_expense(self):
        try:
            date_str = self._parse_date(self.date_entry.get())
            amount = self._parse_amount(self.expense_entry.get())
            if amount <= 0:
                raise ValueError("Expense must be > 0")
            tx = {
                "date": date_str,
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
        except Exception:
            messagebox.showerror("Invalid entry", "Use date format YYYY-MM-DD and a valid expense amount (example: 23.45).")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return

        indices = sorted([int(i) for i in selected], reverse=True)
        for idx in indices:
            self.transactions.pop(idx)

        self.rebuild_month_list()
        self.refresh_table()

    def update_totals(self):
        current_month = self.month_var.get()

        visible = []
        for tx in self.transactions:
            if current_month == "All" or self.month_key(tx["date"]) == current_month:
                visible.append(tx)

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
