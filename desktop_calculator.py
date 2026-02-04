import tkinter as tk


def calculate():
    try:
        a = float(entry_a.get())
        b = float(entry_b.get())
        op = operation.get()

        if op == "Add":
            result = a + b
        elif op == "Subtract":
            result = a - b
        elif op == "Multiply":
            result = a * b
        elif op == "Divide":
            result = a / b
        else:
            result_label.config(text="Pick an operation.")
            return

        result_label.config(text=f"Result: {result}")
    except ValueError:
        result_label.config(text="Please enter valid numbers.")
    except ZeroDivisionError:
        result_label.config(text="Cannot divide by zero.")


root = tk.Tk()
root.title("My Desktop Calculator")

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

# Button + result
tk.Button(root, text="Calculate", command=calculate).grid(row=3, column=0, columnspan=2, pady=12)
result_label = tk.Label(root, text="Result: ")
result_label.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
