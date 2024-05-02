from tkinter import *
from tkinter import simpledialog
import os.path
import sqlite3

# globally checking if database exists
path = './database.db'
dbExists = os.path.isfile(path)

root = Tk()
root.title('Budgeting Application')

# have the user name their categories, and store it
def nameCategories():
    global categoryAmounts  # global variable
    if not dbExists:
        totalMonthlyBudget = monthlyBudget.get()
        totalUserCate = numOfCate.get()

        # Validate text
        if totalMonthlyBudget.isdigit() and totalUserCate.isdigit() and int(totalMonthlyBudget) > 0 and int(totalUserCate) > 0:
            top = Toplevel()
            root.withdraw()  # Hide the root window
            numCategories = int(totalUserCate)
            categoryNames = []
            categoryAmounts = []

            for i in range(numCategories):
                categoryName = simpledialog.askstring("Category Name", f"Enter a name for each spending category, category {i + 1}:")
                if categoryName:
                    categoryNames.append(categoryName)
                else:
                    categoryNames.append(f"Category {i + 1}")  # makes a default name for a category for the user
                amountEntry = Entry(top, width=10)
                amountEntry.grid(row=i, column=1)
                categoryAmounts.append((categoryName, amountEntry))  # Append tuple instead of Entry widget

            def saveAmounts():
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                
                # Construct the column names string for the INSERT statement
                column_names = ','.join(f'category_{i}, amount_{i}' for i in range(1, len(categoryAmounts) + 1))
                # Construct the placeholders string for the values
                value_placeholders = ','.join('?,?' for _ in range(len(categoryAmounts)))  # Two placeholders per category (category and amount)
                
                # Construct the SQL query with dynamic column names and placeholders
                sql = f"INSERT INTO Categories ({column_names}) VALUES ({value_placeholders})"
                
                # Extract category names and amounts from Entry widgets
                category_amounts_flat = []
                for category, entry in categoryAmounts:
                    category_name = category
                    amount = entry.get()
                    category_amounts_flat.extend((category_name, amount))
                
                # Execute the SQL query with the category names and amounts as values
                c.execute(sql, category_amounts_flat)
                
                conn.commit()
                conn.close()

            Button(top, text="Save Amounts", command=saveAmounts).grid(row=7, column=1, columnspan=2)

            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            sql = "CREATE TABLE IF NOT EXISTS Categories ("
            for i, categoryName in enumerate(categoryNames, start=1):
                sql += f"category_{i} TEXT, "
                sql += f"amount_{i} INTEGER, "  # Add amount column for each category
            sql = sql[:-2] + ")"  # Remove the last comma and add closing parenthesis
            c.execute(sql)
            conn.commit()
            conn.close()

            for i, (categoryName, _) in enumerate(categoryAmounts):
                Label(top, text=categoryName).grid(row=i, column=0)
                Entry(top, width=10, textvariable=categoryAmounts[i][1]).grid(row=i, column=1)

            # Button to calculate total
            Button(top, text="Calculate Total", command=lambda: calculateTotal(categoryAmounts)).grid(row=numCategories, column=0, columnspan=2)

            def closeWindow():
                top.destroy()

            Button(top, text="Close", command=closeWindow).grid(row=numCategories + 1, column=0, columnspan=2)
        else:
            ErrorLabel.config(text="Please enter valid values larger than 0.")
    else:
        query()

# Function to display categories
def displayCategories(categoryData):
    top = Toplevel()
    for i, (categoryName, amount) in enumerate(categoryData):
        Label(top, text=categoryName).grid(row=i, column=0)
        Label(top, text=f"Amount: {amount}").grid(row=i, column=1)

# Function to calculate total amount spent
def calculateTotal(amounts):
    total = sum(int(entry.get()) for _, entry in amounts if entry.get().isdigit())
    totalLabel.config(text=f"Total Amount Spent: {total}")

# create a function to get the categories
def query():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Categories")
    records = c.fetchall()
    conn.close()
    # Display categories
    categoryData = []
    for record in records:
        category_name = record[0]
        amounts = [record[i] for i in range(1, len(record))]
        categoryData.append((category_name, amounts))
    displayCategories(categoryData)

if dbExists:
    enterButton = Button(root, text="continue", command=nameCategories)
    enterButton.grid(row=3, column=8, padx=10)
else:
    monthlyBudget = Entry(root, width=35, borderwidth=5)
    monthlyBudget.grid(row=1, column=0, columnspan=20, padx=100, pady=10)
    monthlyBudget.insert(0, "Enter your total monthly budget")

    numOfCate = Entry(root, width=35, borderwidth=5)
    numOfCate.grid(row=2, column=0, columnspan=10, padx=100, pady=10)
    numOfCate.insert(0, "Enter the number of categories")

    # create label for errors may need to make large, red for attention grabbing
    ErrorLabel = Label(root, text="", fg="red")
    ErrorLabel.grid(row=4, column=0, columnspan=10, padx=100, pady=10)

    # label for total spent
    totalLabel = Label(root, text="")
    totalLabel.grid(row=5, column=0, columnspan=2)

    # create button for continuing
    enterButton = Button(root, text="Continue", command=nameCategories)
    enterButton.grid(row=3, column=8, padx=10)

# label for total spent
totalLabel = Label(root, text="")
totalLabel.grid(row=5, column=0, columnspan=2)
root.mainloop()
