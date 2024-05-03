from tkinter import *
from tkinter import simpledialog
import os.path
import sqlite3



# Check if the database exists at the beginning
path = './database.db'
dbExists = os.path.isfile(path)

root = Tk()
root.title('Budgeting Application')

#init monthly budget entry window
#monthlyBudget = Entry(root, width=35, borderwidth=5)
#monthlyBudget.grid(row=1, column=0, columnspan=20, padx=100, pady=10)
#monthlyBudget.insert(0, "Enter your total monthly budget")


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
            top.geometry("600x400")  # Set the size of the window to 600x400 pixels
            root.withdraw()  # Hide the root window
            numCategories = int(totalUserCate) # Need to be intergers to be added later
            categoryAmounts = [] # Init category amounts

            for i in range(numCategories): # Letting the user make the number of categories and name them
                categoryName = simpledialog.askstring("Category Name", f"Enter a name for each spending category, category {i + 1}:")
                categoryName = categoryName if categoryName else f"Category {i + 1}"
                amountVar = StringVar() 
                Entry(top, width=50, textvariable=amountVar).grid(row=i, column=1, columnspan=4, padx=10, pady=10)
                categoryAmounts.append((categoryName, amountVar))

            Button(top, text="Save Amounts", command=create_database).grid(row=numCategories, column=1, columnspan=4, padx=10, pady=10) #commit the amounts
            for i, (categoryName, _) in enumerate(categoryAmounts):
                Label(top, text="Enter amount spent so far in: " + categoryName).grid(row=i, column=0, padx=20)

            #Button(top, text="Calculate Total", command=lambda: calculateTotal(categoryAmounts)).grid(row=numCategories+1, column=0, columnspan=2) #may need removed
            Button(top, text="Close", command=lambda: (top.destroy(), root.destroy())).grid(row=numCategories+6, column=4, columnspan=3) #closes the program
        else:
            ErrorLabel.config(text="Please enter valid values larger than 0.") #input validation

def create_database(): # Create the database where the user information is stored
    global dbExists # Global dbExists for later
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Drop the tables if they exist mostly validation, should not exist if database doesnt exist
    c.execute("DROP TABLE IF EXISTS Categories")
    c.execute("DROP TABLE IF EXISTS Budget")
    # Create the Categories table and the amount row
    c.execute('''CREATE TABLE Categories (
                    category TEXT,
                    amount INTEGER
                )''')
    # create the Budget table to hold the budget
    c.execute('''CREATE TABLE Budget (
                    id INTEGER PRIMARY KEY,
                    amount INTEGER
                )''')
    # Insert the initial budget amount
    c.execute("INSERT INTO Budget (amount) VALUES (?)", (int(monthlyBudget.get()),))
    for category, amountVar in categoryAmounts:
        c.execute("INSERT INTO Categories (category, amount) VALUES (?, ?)", (category, amountVar.get()))
    conn.commit() #commit changes to db
    conn.close()
    dbExists = True # Update dbExists to true to prevent issues with other functions

def displayCategories(categoryData): # put the users categories into labels
    top = Toplevel() #new window
    updates = []
    for i, (categoryName, amount) in enumerate(categoryData):
        Label(top, text=categoryName).grid(row=i, column=0)
        Label(top, text=f"Current Amount: {amount}").grid(row=i, column=1)
        newAmountVar = StringVar()
        Entry(top, width=10, textvariable=newAmountVar).grid(row=i, column=2)
        updates.append((categoryName, amount, newAmountVar))
    
    Button(top, text="Update Amounts", command=lambda: (updateAmounts(updates), top.destroy())).grid(row=len(categoryData), column=1) #updates the amount and destroys the window to prevent accidental repeat entires

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
    conn = sqlite3.connect('database.db') # connect to databse
    c = conn.cursor()
    c.execute("SELECT * FROM Categories") 
    records = c.fetchall() #fetch all records in table categories
    conn.close() #close connection
    categoryData = [(record[0], record[1]) for record in records] #get the records
    displayCategories(categoryData)

def calculateTotal(): #adds up the category amounts
    conn = sqlite3.connect('database.db') #Connect to the databse to get the values
    c = conn.cursor() #cursor
    c.execute("SELECT sum(amount) FROM Categories") #sum to add amounts together
    total = c.fetchone()[0] #fetch
    total = total if total is not None else 0  #None error validation
    totalLabel.config(text=f"Total Amount Spent: {total}")
    conn.close()

def fetchBudget():
    conn = sqlite3.connect('database.db') #conn to db
    c = conn.cursor()
    c.execute("SELECT amount FROM Budget ORDER BY id DESC LIMIT 1") #only need one
    result = c.fetchone() #fetch one result
    if result: #should always be a result, validation
        budgetLabel.config(text=f"Your Monthly Budget is: {result[0]}")  # Update the label text
    conn.close()

if dbExists:
    
    enterButton = Button(root, text="Show/add to categories", command=query) #seems to refresh the update button, also needs fixing
    enterButton.grid(row=2, column=0, padx=10, pady=39)
    totalButton = Button(root, text="Show Total Amount", command=calculateTotal)
    totalButton.grid(row=6, column=0, columnspan=2, pady=30)
    #init fetch budget button
    budgetLabel = Label(root, text="Your Monthly Budget is: ", font=('Arial', 24))
    budgetLabel.grid(row=0, column=0, columnspan=2, sticky=W, padx=10, pady=10)
    fetchBudget() #fetch the orginal budget

else:
    monthlyBudget = Entry(root, width=35, borderwidth=5)
    monthlyBudget.grid(row=1, column=0, columnspan=20, padx=100, pady=50)
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