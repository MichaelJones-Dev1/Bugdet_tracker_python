from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
import json
import os
import sys

#Lets the build find the asset file
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

#Name of the save data file
dataFile = "data.json"

#Load the data into the app for later use
def load_all_data():
    if not os.path.exists(dataFile):
        return {}
    with open(dataFile, "r") as f:
        return json.load(f)

#save button function
def save_value(rowFrame, newName, newAmount):
    data = load_all_data()

    oldName = rowFrame.orignalName

    # If the name changed, delete the old key
    if oldName in data and oldName != newName:
        del data[oldName]
    
    #Save the new key/value pair
    data[newName] = newAmount

    rowFrame.orignalName = newName

    with open(dataFile, "w") as f:
        json.dump(data, f, indent=4)

#delete button function
def delete_value(key):
    data = load_all_data()
    if key in data:
        del data[key]
        with open(dataFile, "w") as f:
            json.dump(data, f, indent=4)

#Adds the values already stored in the data file onto the screen on startup
def addValues():
    data = load_all_data()
    for name, amount in data.items():
        addBIllRow(name, amount)

#All logic for the bill row creation
def addBIllRow(name="", amount=""):
    rowFrame = ttk.Frame(billFrame, style="MainFrame.TFrame")

    rowFrame.orignalName = name
    billName = StringVar(value=name)
    billCost = StringVar(value=amount)

    billNameEntry = Entry(rowFrame, textvariable=billName, width=20, **entryStyles)
    billNameEntry.grid(row=0, column=0, padx=5)
    billCostEntry = Entry(rowFrame, textvariable=billCost, width=10, **entryStyles)
    billCostEntry.grid(row=0, column=1, padx=5)

    def schedule_autosave():
        if hasattr(rowFrame, "autosave_after_id"):
            rowFrame.after_cancel(rowFrame.autosave_after_id)

        rowFrame.autosave_after_id = rowFrame.after(
            400,  # milliseconds
            lambda: (save_value(rowFrame, billName.get(), billCost.get()), totalBillCost())
    )

    billNameEntry.bind("<KeyRelease>", lambda e: schedule_autosave())
    billCostEntry.bind("<KeyRelease>", lambda e: schedule_autosave())

    deleteButton = ttk.Button(rowFrame, image=XMark, command=lambda: (remove_bill_row(rowFrame, rowFrame.orignalName), totalBillCost()), style="BlueButton.TButton")
    deleteButton.grid(row=0, column=2, padx=12, pady=2)

    rowFrame.pack(anchor="w", pady=3)

    billRows.append(rowFrame)

#Logic to remove a bill row
def remove_bill_row(row_frame, billName):
    row_frame.destroy()
    billRows.remove(row_frame)
    delete_value(billName)

#Finds the total cost of all bills by adding the amounts from the data file
def totalBillCost():
    total = 0
    data = load_all_data()
    for name, amount in data.items():
        try:
            total += int(amount)
        except:
            pass  # ignore non-numeric values

    totalCost.set(total)
 
#Find remaining balance
def remainingBalanceFun():
    try:
        curr = int(currentBalance.get())
    except:
        curr = 0

    try:
        exp = int(totalCost.get())
    except:
        exp = 0

    remainingBalance.set(curr - exp)

#Basic Setup
root = Tk()
root.title("Monthly Finance Calculator")
root.resizable(False, False)

#Image setup
checkMarkIMG = PhotoImage(file=resource_path("assets/checkMarkIMG.png"))
checkMarkIMG = checkMarkIMG.subsample(16,16)
XMark = PhotoImage(file=resource_path("assets/XMark.png"))
XMark = XMark.subsample(16,16)

#Creates the main screen
mainframe = ttk.Frame(root, style="MainFrame.TFrame")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

#Creates the Header Bar
headerBar = ttk.Frame(mainframe, style="MainFrame.TFrame")
headerBar.grid(column=0, row=0, columnspan=3, sticky="ew")

#Creates the row of Headers describing what each entry does
headerRow = ttk.Frame(mainframe, style="MainFrame.TFrame")
headerRow.grid(column=0, row=2, columnspan=3, sticky="w", pady=(10, 0))

# Scrollable bill list setup
billCanvas = Canvas(mainframe, bg="#000000", highlightthickness=0)
billScrollbar = ttk.Scrollbar(mainframe, orient="vertical", command=billCanvas.yview)
billFrame = ttk.Frame(billCanvas, style="MainFrame.TFrame")
billFrame.bind("<Configure>", lambda e: billCanvas.configure(scrollregion=billCanvas.bbox("all")))
billCanvas.create_window((0, 0), window=billFrame, anchor="nw")
billCanvas.configure(yscrollcommand=billScrollbar.set)

#Binds the scroll wheel to the scroll bar
def _on_mousewheel(event):
    billCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

billCanvas.bind_all("<MouseWheel>", _on_mousewheel)

# Layout
billCanvas.grid(row=3, column=0, columnspan=3, sticky="nsew")
billScrollbar.grid(row=3, column=3, sticky="ns")


#Custom Fonts and styles
entryFonts = tkFont.Font(family="Arial", size=20)
entryStyles = {
    "bg" : "#000000",
    "fg" : "#4CC7F8",
    "insertbackground" : "#4CC7F8",
    "font" : entryFonts
}
style = ttk.Style()
style.theme_use("clam")
style.configure("BlueButton.TButton", background="#000000",  relief="flat", foreground="#4CC7F8", borderwidth=2, focusthickness=3, focuscolor="none", font=("Arial", 20))
style.map("BlueButton.TButton", background=[("active", "#363636")], foreground=[("active", "#4CC7F8")])
style.configure("MainFrame.TFrame", background="#000000")
style.configure("Text.TLabel", font=("Arial", 20), foreground="#4CC7F8", background="#000000")

#Contains all the rows off bills the user creates
billRows = []

#HeaderBar
appTitle = ttk.Label(headerBar, text="My Monthly Planner", style="Text.TLabel", font=("Arial", 28, "bold"))
appTitle.grid(column=0, row=0, sticky="w")
versionLabel = ttk.Label(headerBar, text="v1.0", style="Text.TLabel", font=("Arial", 10, "bold"))
versionLabel.grid(column=1, row=0, sticky="ws")
divider = ttk.Separator(mainframe, orient="horizontal")
divider.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(5, 10))

#HeaderRow
billNameHeader = ttk.Label(headerRow, text="BILL NAME", style="Text.TLabel", font=("Arial", 18, "bold"), width=23)
billNameHeader.grid(row=0, column=0, padx=5)

billCostHeader = ttk.Label(headerRow, text="BILL COST", style="Text.TLabel", font=("Arial", 18, "bold"), width=12)
billCostHeader.grid(row=0, column=1, padx=5)

deleteHeader = ttk.Label(headerRow, text="DELETE", style="Text.TLabel", font=("Arial", 18, "bold"))
deleteHeader.grid(row=0, column=3, padx=5)

#CurrentBalance Setup
currentBalance = StringVar()
balanceLabel = ttk.Label(mainframe, text="Current Balance", style="Text.TLabel")
balanceLabel.grid(column=0, row=5, sticky="e")
balanceEntry = Entry(mainframe, textvariable=currentBalance, **entryStyles, width=7)
balanceEntry.grid(column=1, row=5, sticky="w")

#Remaining balance Setup
remainingBalance = StringVar()
remainingLabel = ttk.Label(mainframe, text="Remaining Balance", style="Text.TLabel")
remainingLabel.grid(column=0, row=7, sticky="e")
dynamicRemainingLabel = ttk.Label(mainframe, textvariable=remainingBalance, style="Text.TLabel")
dynamicRemainingLabel.grid(column=1, row=7, sticky="w")

#Controls the auto calculation for the remaining balance
def schedule_autosave():
    if hasattr(mainframe, "autosave_after_id"):
        mainframe.after_cancel(mainframe.autosave_after_id)

    mainframe.autosave_after_id = mainframe.after(
        400,  # milliseconds
        lambda: remainingBalanceFun(currentBalance, totalCost)
)

balanceEntry.bind("<KeyRelease>", lambda e: remainingBalanceFun())


#Description for Total Cost
expensesLabal = ttk.Label(mainframe, text="Total Expenses", style="Text.TLabel")
expensesLabal.grid(column=0, row=6, sticky="e")

#The total cost label that dynamiclly changes
totalCost = IntVar()
totalLabel = ttk.Label(mainframe, textvariable=totalCost, style="Text.TLabel")
totalLabel.grid(column=1, row=6, sticky="w")

#Button to add an additional row of bills
addButtonLabel = ttk.Label(mainframe, text="Add Bill", style="Text.TLabel")
addButtonLabel.grid(column=0, row=8, sticky="e")
addButton = ttk.Button(mainframe, image=checkMarkIMG, style="BlueButton.TButton", command=addBIllRow)
addButton.grid(column=1, row=8, sticky="w")

#Perform base padding on each widget
for child in mainframe.winfo_children(): 
   child.grid_configure(padx=5, pady=5)

mainframe.rowconfigure(3, weight=1)
mainframe.columnconfigure(0, weight=1)

addValues()
totalBillCost()
root.mainloop()
