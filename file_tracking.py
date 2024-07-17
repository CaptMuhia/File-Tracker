import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import csv

# Connect to SQLite database
conn = sqlite3.connect('file_tracking.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                file_name TEXT NOT NULL,
                unique_number TEXT NOT NULL
             )''')

c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                department TEXT NOT NULL
             )''')

c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                file_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                date_taken TEXT NOT NULL,
                date_returned TEXT,
                condition TEXT,
                FOREIGN KEY (file_id) REFERENCES files(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
             )''')

conn.commit()

# Tkinter GUI setup
root = tk.Tk()
root.title("File Tracking System")
root.geometry("800x600")

# Helper functions
def register_file():
    file_name = file_name_entry.get()
    unique_number = unique_number_entry.get()
    
    if file_name and unique_number:
        c.execute("INSERT INTO files (file_name, unique_number) VALUES (?, ?)", (file_name, unique_number))
        conn.commit()
        messagebox.showinfo("Success", "File registered successfully!")
        file_name_entry.delete(0, tk.END)
        unique_number_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input error", "Please fill in all fields")

def register_user():
    first_name = first_name_entry.get()
    last_name = last_name_entry.get()
    department = department_entry.get()
    
    if first_name and last_name and department:
        c.execute("INSERT INTO users (first_name, last_name, department) VALUES (?, ?, ?)", (first_name, last_name, department))
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully!")
        first_name_entry.delete(0, tk.END)
        last_name_entry.delete(0, tk.END)
        department_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input error", "Please fill in all fields")

def lend_file():
    file_id = file_combobox.get().split(" - ")[0]
    user_id = user_combobox.get().split(" - ")[0]
    date_taken = date_taken_entry.get_date().strftime("%Y-%m-%d")

    if file_id and user_id and date_taken:
        c.execute("INSERT INTO transactions (file_id, user_id, date_taken) VALUES (?, ?, ?)",
                  (file_id, user_id, date_taken))
        conn.commit()
        messagebox.showinfo("Success", "File lent out successfully!")
        file_combobox.set("")
        user_combobox.set("")
        date_taken_entry.set_date(datetime.now())
        load_data()  # Refresh the comboboxes
    else:
        messagebox.showwarning("Input error", "Please fill in all fields")

def return_file():
    transaction_id = return_transaction_combobox.get().split(" - ")[0]
    date_returned = date_returned_entry.get_date().strftime("%Y-%m-%d")
    condition = condition_entry.get()
    
    if transaction_id and date_returned:
        c.execute("UPDATE transactions SET date_returned = ?, condition = ? WHERE id = ?",
                  (date_returned, condition, transaction_id))
        conn.commit()
        messagebox.showinfo("Success", "File returned successfully!")
        return_transaction_combobox.set("")
        date_returned_entry.set_date(datetime.now())
        condition_entry.delete(0, tk.END)
        load_data()  # Refresh the comboboxes
    else:
        messagebox.showwarning("Input error", "Please fill in all fields")

def load_data():
    c.execute("SELECT id, file_name FROM files")
    files = c.fetchall()
    file_combobox['values'] = [f"{file[0]} - {file[1]}" for file in files]

    c.execute("SELECT id, first_name, last_name FROM users")
    users = c.fetchall()
    user_combobox['values'] = [f"{user[0]} - {user[1]} {user[2]}" for user in users]

    c.execute("SELECT t.id, u.first_name, u.last_name, f.file_name, t.date_taken FROM transactions t JOIN users u ON t.user_id = u.id JOIN files f ON t.file_id = f.id WHERE t.date_returned IS NULL")
    transactions = c.fetchall()
    return_transaction_combobox['values'] = [f"{transaction[0]} - {transaction[1]} {transaction[2]} - {transaction[3]} (Taken: {transaction[4]})" for transaction in transactions]

def generate_report():
    c.execute("SELECT t.id, f.file_name, u.first_name, u.last_name, t.date_taken, t.date_returned, t.condition FROM transactions t JOIN files f ON t.file_id = f.id JOIN users u ON t.user_id = u.id")
    transactions = c.fetchall()
    
    with open("file_tracking_report.csv", "w", newline='') as csvfile:
        fieldnames = ["Transaction ID", "File Name", "User First Name", "User Last Name", "Date Taken", "Date Returned", "Condition"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for t in transactions:
            writer.writerow({
                "Transaction ID": t[0],
                "File Name": t[1],
                "User First Name": t[2],
                "User Last Name": t[3],
                "Date Taken": t[4],
                "Date Returned": t[5],
                "Condition": t[6]
            })
    
    messagebox.showinfo("Success", "Report generated successfully!")

# Tabs
tab_control = ttk.Notebook(root)
register_file_tab = ttk.Frame(tab_control)
register_user_tab = ttk.Frame(tab_control)
lend_file_tab = ttk.Frame(tab_control)
return_file_tab = ttk.Frame(tab_control)

tab_control.add(register_file_tab, text="Register File")
tab_control.add(register_user_tab, text="Register User")
tab_control.add(lend_file_tab, text="Lend File")
tab_control.add(return_file_tab, text="Return File")
tab_control.pack(expand=1, fill="both")

# Register File Tab
ttk.Label(register_file_tab, text="File Name:").grid(column=0, row=0, padx=10, pady=10)
file_name_entry = ttk.Entry(register_file_tab)
file_name_entry.grid(column=1, row=0, padx=10, pady=10)

ttk.Label(register_file_tab, text="Unique Number:").grid(column=0, row=1, padx=10, pady=10)
unique_number_entry = ttk.Entry(register_file_tab)
unique_number_entry.grid(column=1, row=1, padx=10, pady=10)

ttk.Button(register_file_tab, text="Register File", command=register_file).grid(column=1, row=2, padx=10, pady=10)

# Register User Tab
ttk.Label(register_user_tab, text="First Name:").grid(column=0, row=0, padx=10, pady=10)
first_name_entry = ttk.Entry(register_user_tab)
first_name_entry.grid(column=1, row=0, padx=10, pady=10)

ttk.Label(register_user_tab, text="Last Name:").grid(column=0, row=1, padx=10, pady=10)
last_name_entry = ttk.Entry(register_user_tab)
last_name_entry.grid(column=1, row=1, padx=10, pady=10)

ttk.Label(register_user_tab, text="Department:").grid(column=0, row=2, padx=10, pady=10)
department_entry = ttk.Entry(register_user_tab)
department_entry.grid(column=1, row=2, padx=10, pady=10)

ttk.Button(register_user_tab, text="Register User", command=register_user).grid(column=1, row=3, padx=10, pady=10)

# Lend File Tab
ttk.Label(lend_file_tab, text="Select File:").grid(column=0, row=0, padx=10, pady=10)
file_combobox = ttk.Combobox(lend_file_tab)
file_combobox.grid(column=1, row=0, padx=10, pady=10)

ttk.Label(lend_file_tab, text="Select User:").grid(column=0, row=1, padx=10, pady=10)
user_combobox = ttk.Combobox(lend_file_tab)
user_combobox.grid(column=1, row=1, padx=10, pady=10)

ttk.Label(lend_file_tab, text="Date Taken:").grid(column=0, row=2, padx=10, pady=10)
date_taken_entry = DateEntry(lend_file_tab, date_pattern='y-mm-dd')
date_taken_entry.grid(column=1, row=2, padx=10, pady=10)

ttk.Button(lend_file_tab, text="Lend File", command=lend_file).grid(column=1, row=3, padx=10, pady=10)
ttk.Button(lend_file_tab, text="Refresh", command=load_data).grid(column=1, row=4, padx=10, pady=10)

# Return File Tab
ttk.Label(return_file_tab, text="Select Transaction:").grid(column=0, row=0, padx=10, pady=10)
return_transaction_combobox = ttk.Combobox(return_file_tab)
return_transaction_combobox.grid(column=1, row=0, padx=10, pady=10)

ttk.Label(return_file_tab, text="Date Returned:").grid(column=0, row=1, padx=10, pady=10)
date_returned_entry = DateEntry(return_file_tab, date_pattern='y-mm-dd')
date_returned_entry.grid(column=1, row=1, padx=10, pady=10)

ttk.Label(return_file_tab, text="Condition:").grid(column=0, row=2, padx=10, pady=10)
condition_entry = ttk.Entry(return_file_tab)
condition_entry.grid(column=1, row=2, padx=10, pady=10)

ttk.Button(return_file_tab, text="Return File", command=return_file).grid(column=1, row=3, padx=10, pady=10)

# Report Generation
ttk.Button(root, text="Generate Report", command=generate_report).pack(pady=10)

# Load initial data
load_data()

root.mainloop()