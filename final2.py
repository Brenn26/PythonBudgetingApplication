from tkinter import *
from tkinter import simpledialog
import os.path
import sqlite3

# Check if the database exists at the beginning
path = './database.db'
dbExists = os.path.isfile(path)

root = Tk()
root.title('Budgeting Application')

# Initialize categoryAmounts globally
categoryAmounts = []

# Function to handle category naming and storing
def nameCategories():
    global categoryAmounts, dbExists  # Global variable
    if not dbExists:
        totalMonthlyBudget = monthlyBudget.get()
        totalUserCate = numOfCate.get()

        if totalMonthlyBudget.isdigit() and totalUserCate.isdigit() and int(totalMonthlyBudget) > 0 and int(totalUserCate) > 0:
            top = Toplevel()
            root.withdraw()  # Hide the root window
            numCategories = int(totalUserCate) # Need to be intergers to be added later
            categoryAmounts = [] # Init category amounts

            for i in range(numCategories): # Letting the user make the number of categories and name them
                categoryName = simpledialog.askstring("Category Name", f"Enter a name for each spending category, category {i + 1}:")
                categoryName = categoryName if categoryName else f"Category {i + 1}"
                amountVar = StringVar()
                Entry(top, width=10, textvariable=amountVar).grid(row=i, column=1)
                categoryAmounts.append((categoryName, amountVar))

            Button(top, text="Save Amounts", command=create_database).grid(row=numCategories, column=1, columnspan=2) #commit the amounts
            for i, (categoryName, _) in enumerate(categoryAmounts):
                Label(top, text=categoryName).grid(row=i, column=0)

            Button(top, text="Calculate Total", command=lambda: calculateTotal(categoryAmounts)).grid(row=numCategories+1, column=0, columnspan=2) #may need removed
            Button(top, text="Close", command=top.destroy).grid(row=numCategories+2, column=0, columnspan=2)
        else:
            ErrorLabel.config(text="Please enter valid values larger than 0.") #input validation

def create_database(): #make the db to store the user information, only need it once
    global dbExists
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS Categories")
    c.execute('''CREATE TABLE Categories (
                    category TEXT,
                    amount INTEGER
                )''')
    for category, amountVar in categoryAmounts:
        amount = amountVar.get()
        c.execute("INSERT INTO Categories (category, amount) VALUES (?, ?)", (category, amount))
    conn.commit()
    conn.close()
    dbExists = True  # Update the dbExists flag after creating the database to stop unexpected things from happening 

def displayCategories(categoryData): #put the users categories into labels
    top = Toplevel()
    updates = []
    for i, (categoryName, amount) in enumerate(categoryData):
        Label(top, text=categoryName).grid(row=i, column=0)
        Label(top, text=f"Current Amount: {amount}").grid(row=i, column=1)
        newAmountVar = StringVar()
        Entry(top, width=10, textvariable=newAmountVar).grid(row=i, column=2)
        updates.append((categoryName, amount, newAmountVar))
    
    Button(top, text="Update Amounts", command=lambda: updateAmounts(updates)).grid(row=len(categoryData), column=1)

def updateAmounts(updates): # Let the user update the spent amount
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    for category, old_amount, amountVar in updates: #Changed naming convention to keep track of updates, may need better system
        if amountVar.get().isdigit():
            new_amount = int(old_amount) + int(amountVar.get())
            c.execute("UPDATE Categories SET amount = ? WHERE category = ?", (new_amount, category))
    conn.commit()
    conn.close()

def query(): # Query the existing db
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Categories")
    records = c.fetchall()
    conn.close()
    categoryData = [(record[0], record[1]) for record in records]
    displayCategories(categoryData)

def calculateTotal(amounts): #May need removed or changed, doesnt seem to work right yet
    total = sum(int(amountVar.get()) for _, amountVar in amounts if amountVar.get().isdigit())
    totalLabel.config(text=f"Total Amount Spent: {total}")

if dbExists:
    enterButton = Button(root, text="Continue", command=query) #seems to refresh the update button, also needs fixing
    enterButton.grid(row=3, column=8, padx=10)
else:
    monthlyBudget = Entry(root, width=35, borderwidth=5)
    monthlyBudget.grid(row=1, column=0, columnspan=20, padx=100, pady=10)
    monthlyBudget.insert(0, "Enter your total monthly budget")

    numOfCate = Entry(root, width=35, borderwidth=5)
    numOfCate.grid(row=2, column=0, columnspan=10, padx=100, pady=10)
    numOfCate.insert(0, "Enter the number of categories")

    ErrorLabel = Label(root, text="", fg="red") #made error red for visibility
    ErrorLabel.grid(row=4, column=0, columnspan=10, padx=100, pady=10)

    enterButton = Button(root, text="Continue", command=nameCategories) # Only ran if dbExists is false
    enterButton.grid(row=3, column=8, padx=10)

totalLabel = Label(root, text="") # Label init, I think this may actualy be vestigal 
totalLabel.grid(row=5, column=0, columnspan=2)
root.mainloop()