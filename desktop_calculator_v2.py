import tkinter as tk


def calculate():
    try:
        a = float(entry_a.get())
        b = float(entry_b.get())
        op = operation.get()

        if op == "Add":
            result = a + b
            symbol = "+"
        elif op == "Subtract":
            result = a - b
            symbol = "-"
        elif op == "Multiply":
            result = a * b
            symbol = "×"
        elif op == "Divide":
            result = a / b
            symbol = "÷"
        else:
            result_label.config(text="Pick an operation.")
            return

        result_label.config(text=f"Result: {a} {symbol} {b} = {result}")
        history_list.insert(tk.END, f"{a} {symbol} {b} = {result}")
    except ValueError:
        result_label.config(text="Please enter valid numbers.")
    except ZeroDivisionError:
        result_label.config(text="Cannot divide by zero.")


def clear():
    entry_a.delete(0, tk.END)
    entry_b.delete(0, tk.END)
    operation.set("Add")
    result_label.config(text="Result:")
    entry_a.focus_set()


root = tk.Tk()
root.title("My Desktop Calculator v2")

# Inputs
tk.Label(root, text="First number:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
entry_a = tk.Entry(root, width=20)
entry_a.grid(row=0, column=1, padx=10, pady=8)

tk.Label(root, text="Second number:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
entry_b = tk.Entry(root, width=20)
entry_b.grid(row=1, column=1, padx=10, pady=8)

# Operation dropdown
operation = tk.StringVar(value="Add")
ops = ["Add", "Subtract", "Multiply", "Divide"]
tk.Label(root, text="Operation:").grid(row=2, column=0, padx=10, pady=8, sticky="e")
tk.OptionMenu(root, operation, *ops).grid(row=2, column=1, padx=10, pady=8, sticky="w")

# Buttons
button_frame = tk.Frame(root)
button_frame.grid(row=3, column=0, columnspan=2, pady=10)

tk.Button(button_frame, text="Calculate", command=calculate, width=12).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Clear", command=clear, width=12).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Quit", command=root.destroy, width=12).grid(row=0, column=2, padx=5)

# Result
result_label = tk.Label(root, text="Result:")
result_label.grid(row=4, column=0, columnspan=2, pady=8)

# History
tk.Label(root, text="History:").grid(row=5, column=0, padx=10, pady=6, sticky="ne")
history_list = tk.Listbox(root, width=35, height=6)
history_list.grid(row=5, column=1, padx=10, pady=6, sticky="w")

clear()
root.mainloop()
