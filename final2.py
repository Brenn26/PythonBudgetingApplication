from tkinter import *

root = Tk()
root.title('Budgeting Application')


#have the user name their categories, will need a way to store this
#for now create second screen for categories, this may cause an issue with the varibles later and may need to be changed

def nameCategories():
    totalMonthlyBudget = monthlyBudget.get()
    totalUserCate = numOfCate.get()

    # Validate text
    if totalMonthlyBudget.isdigit() and totalUserCate.isdigit() and int(totalMonthlyBudget) > 0 and int(totalUserCate) > 0:
        top = Toplevel()
        root.withdraw()  # Hide the root window
        numCategories = int(totalUserCate)
        for i in range(numCategories):
            label = Label(top, text=f"Name of category {i+1}:")
            label.grid(row=i, column=0, padx=10, pady=5)
            entry = Entry(top, width=20, borderwidth=3)
            entry.grid(row=i, column=1, padx=10, pady=5)
    else:
        ErrorLabel.config(text="Please enter valid values larger than 0.")

#creating entry
#need to find a way to allow the user to create categories and have them be updated in the future making a database may be the easiest option or writing to text a file
#this  DOES  show a new screen, which would satisify the project reqs

monthlyBudget = Entry(root, width=35, borderwidth=5)
monthlyBudget = Entry(root, width=35, borderwidth=5)
monthlyBudget.grid(row=1, column=0, columnspan=20, padx=100, pady=10)
monthlyBudget.insert(0, "Enter your total monthly budget")

numOfCate = Entry(root, width=35, borderwidth=5)
numOfCate.grid(row=2, column=0, columnspan=10, padx=100, pady=10)
numOfCate.insert(0, "Enter the number of categories")

#create label for errors may need to make large, red for attention grabbing
ErrorLabel = Label(root, text="", fg="red")
ErrorLabel.grid(row=4, column=0, columnspan=10, padx=100, pady=10)

#create button for continuing
enterButton = Button(root, text="Continue", command=nameCategories)
enterButton.grid(row=3, column=8, padx=10)

root.mainloop()