while True:
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))

    print("Choose an operation:")
    print("1 = Add")
    print("2 = Subtract")
    print("3 = Multiply")
    print("4 = Divide")
    print("5 = Quit")

    choice = input("Enter choice (1/2/3/4/5): ")

    if choice == "1":
        print("Result:", num1 + num2)
    elif choice == "2":
        print("Result:", num1 - num2)
    elif choice == "3":
        print("Result:", num1 * num2)
    elif choice == "4":
        print("Result:", num1 / num2)
    elif choice == "5":
        print("Goodbye!")
        break
    else:
        print("Invalid choice")

    print()  # blank line for readability
