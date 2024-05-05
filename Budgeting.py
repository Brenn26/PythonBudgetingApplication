from tkinter import *
from tkinter import simpledialog, messagebox, PhotoImage
from PIL import Image, ImageTk

import os.path
import sqlite3



# Check if the database exists at the beginning
path = './database.db' #path of db is local for easy location
dbExists = os.path.isfile(path) # Calling dbesixsts here to be used by other functions

root = Tk() # Start root Window
root.title('Budgeting Application') # Name of application
root.iconbitmap('./dollar.ico') #image one



# Tooltip for alternate tex for the images
tooltip = Label(root, text="", background="yellow", font=("Arial", 8), relief="solid", borderwidth=1)
tooltip.pack_forget()  # Initially hidden

# Function to show tooltip
def showTooltip(event, text):
    tooltip.config(text=text)
    tooltip.place(x=event.x_root - root.winfo_rootx() + 10, y=event.y_root - root.winfo_rooty() + 10)

# Function to hide tooltip
def hideTooltip(event):
    tooltip.place_forget()



#load images
checkmarkImage = Image.open("./checkmark.png")
crossImage = Image.open("./cross.png")

# resize images
tk_checkmark = ImageTk.PhotoImage(checkmarkImage.resize((24, 24), Image.LANCZOS))
tk_cross = ImageTk.PhotoImage(crossImage.resize((24, 24), Image.LANCZOS))

# Initialize categoryAmounts globally
categoryAmounts = []

# Function to handle category naming and storing
def nameCategories():
    global categoryAmounts, dbExists  # Global variable
    if not dbExists: # reverse logic for creation of db
        totalMonthlyBudget = monthlyBudget.get() # Get the entry
        totalUserCate = numOfCate.get() #get the entry for number of categories

        if totalMonthlyBudget.isdigit() and totalUserCate.isdigit() and int(totalMonthlyBudget) > 0 and int(totalUserCate) > 0:
            top = Toplevel() # Make a new window
            top.geometry("600x400")  # Set the size of the window to 600x400 pixels
            root.withdraw()  # Hide the root window
            numCategories = int(totalUserCate) # Need to be intergers error if not
            categoryAmounts = [] # Init category amounts

            for i in range(numCategories): # Letting the user make the number of categories and name them
                categoryName = simpledialog.askstring("Category Name", f"Enter a name for each spending category, category {i + 1}:") # Let the user name their category
                categoryName = categoryName if categoryName else f"Category {i + 1}" #make a default category name if the user doesnt enter anything
                amountVar = StringVar() # String to be retrieved later
                Entry(top, width=50, textvariable=amountVar).grid(row=i, column=1, columnspan=4, padx=10, pady=10)
                categoryAmounts.append((categoryName, amountVar))

            Button(top, text="Save Amounts", command=create_database).grid(row=numCategories, column=1, columnspan=4, padx=10, pady=10) #commit the amounts to the database
            for i, (categoryName, _) in enumerate(categoryAmounts):
                Label(top, text="Enter amount spent so far in: " + categoryName).grid(row=i, column=0, padx=20) 

            
            Button(top, text="Close", command=lambda: (top.destroy(), root.destroy())).grid(row=numCategories+6, column=4, columnspan=3) #closes the program
        else:
            ErrorLabel.config(text="Please enter valid values larger than 0.") #input validation

def create_database(): # Create the database where the user information is stored
    global dbExists # Global dbExists for later
    conn = sqlite3.connect('database.db') #connect to db
    c = conn.cursor() #cursor to interact with db
    # Drop the tables if they exist mostly validation, should not exist if database doesnt exist
    c.execute("DROP TABLE IF EXISTS Categories") # Validation again, deleteing tables 
    c.execute("DROP TABLE IF EXISTS Budget") # Validation again, deleteing tables 
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
    conn.close() # Close the connection to db
    dbExists = True # Update dbExists to true to prevent issues with other functions


def deleteDatabase():  # Function to delete the database so the next months budget can be created
    global dbExists #calling dbexists global again
    if messagebox.askyesno("Delete Confirmation", "Are you sure you want to delete the database? This is permanent and will reset the app"): # Classic are you sure mesasge to prevent accidental data loss
     if os.path.isfile('database.db'):
        os.remove('database.db')
        root.destroy() # kill the program to force a restart

def displayCategories(categoryData): # put the users categories into labels and allow them to enter an amount spent 
    top = Toplevel() #new window for the categories
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
            new_amount = int(old_amount) + int(amountVar.get()) #make sure they are numbers and add the "old amount" to the entry
            c.execute("UPDATE Categories SET amount = ? WHERE category = ?", (new_amount, category)) #add new amounts to db
    conn.commit() #commit changes
    conn.close() # Close database
    

def query(): # Query the existing db
    conn = sqlite3.connect('database.db') # connect to databse
    c = conn.cursor() #cursor
    c.execute("SELECT * FROM Categories") 
    records = c.fetchall() #fetch all records in table categories
    conn.close() #close connection
    categoryData = [(record[0], record[1]) for record in records] #get the records
    displayCategories(categoryData) #run display function

def calculateTotal(): #adds up the category amounts
    conn = sqlite3.connect('database.db') #Connect to the databse to get the values
    c = conn.cursor() #cursor
    c.execute("SELECT sum(amount) FROM Categories") #sum to add amounts together
    total = c.fetchone()[0] #fetch
    total = total if total is not None else 0  #None error validation, math need number
    totalLabel.config(text=f"Total Amount Spent: {total}")
    conn.close()

# Shows the users remaining Amount by getting the amounts from the db adding them, and subtracting by the monthly budget orginally entered
def calcRemainBudget(): 
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT amount FROM Budget ORDER BY id DESC LIMIT 1") # Get the amounts 
    budget = c.fetchone()[0]
    c.execute("SELECT sum(amount) FROM Categories")
    totalSpent = c.fetchone()[0]
    totalSpent = totalSpent if totalSpent is not None else 0 # Cant do math without numbers, validation
    remainingBudget = budget - totalSpent
    remainingLabel.config(text=f"Remaining Budget: {remainingBudget}") # Updates label dynamically 
    # Set the status icon based on whether the user is over or under budget
    if remainingBudget >= 0:
        statusImage.config(image=tk_checkmark)
        statusImage.bind("<Enter>", lambda e: showTooltip(e, "Under Budget")) # Mouse hover
        statusImage.bind("<Leave>", hideTooltip)
    else:
        statusImage.config(image=tk_cross)
        statusImage.bind("<Enter>", lambda e: showTooltip(e, "Over Budget")) # Repeated for other image
        statusImage.bind("<Leave>", hideTooltip)
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
    
    enterButton = Button(root, text="Show/add to categories", command=query) #shows categories to add amount spent
    enterButton.grid(row=2, column=0,  columnspan=2, pady=30)
    totalButton = Button(root, text="Show Total Amount", command=calculateTotal) #calcs the total
    totalButton.grid(row=6, column=0, columnspan=2, pady=30)
    remainingButton = Button(root, text="Show Budget Remaining", command=calcRemainBudget) # Get the remaminging budget
    remainingLabel = Label(root, text="", font=('Arial', 14))
    remainingButton.grid(row=7, column=0, columnspan=2)
    remainingLabel.grid(row=8, column=0, columnspan=2, pady=20)
    deleteButton = Button(root, text="Delete Database", command=deleteDatabase) #button to delete databse and restart the app
    deleteButton.grid(row=10, column=0, columnspan=2, pady=20)
    statusImage = Label(root, image='')
    statusImage.grid(row=9, column=0, columnspan=2)
    #init fetch budget button
    budgetLabel = Label(root, text="Your Monthly Budget is: ", font=('Arial', 15)) 
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

totalLabel = Label(root, text="") # Label init
totalLabel.grid(row=5, column=0, columnspan=2)
root.mainloop() #main loop