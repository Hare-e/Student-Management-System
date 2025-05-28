import tkinter as tk
from tkinter import font, messagebox, ttk, Toplevel
from collections import defaultdict
import csv
import os
import re

CSV_STUDENTS = "students.csv"
CSV_COLLEGES = "colleges.csv"
CSV_PROGRAMS = "programs.csv"

def populate_form(student_data):
    id_no.delete(0, END)
    id_no.insert(0, student_data[0])

    last_name.delete(0, END)
    last_name.insert(0, student_data[1])

    first_name.delete(0, END)
    first_name.insert(0, student_data[2])

    gender_filter.set(student_data[3])
    year_dropdown.set(student_data[4])
    college_filter.set(student_data[5])  

    if student_data[5] in college_names:  
        program_filter["values"] = college_names[student_data[5]]
    else:
        program_filter["values"] = []

    program_filter.set(student_data[6]) 

def find_student_in_csv(student_id):

    try:
        with open("students.csv", mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == student_id:
                    return row 
    except FileNotFoundError:
        messagebox.showerror("Error", "CSV file not found.")
    return None

def save_to_csv(update_mode=False, old_id=None):
    global saved_label, students

    file_path = "students.csv"
    headers = ["ID No.", "Last Name", "First Name", "Gender", "Year Level", "College", "Program"]

    student_id = id_no.get().strip()
    last_name_value = last_name.get().strip().title()
    first_name_value = first_name.get().strip().title()

    student_data = [
        student_id,
        last_name_value,
        first_name_value,
        gender_filter.get(),
        year_dropdown.get(),
        college_filter.get(),
        program_filter.get()
    ]

    validate_student_data()
    if errors:
        messagebox.showerror("Form Error", "There are errors in your form:\n\n" + "\n".join(errors))
        return

    file_exists = os.path.exists(file_path)
    updated_rows = []
    existing_student = None

    if file_exists:
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)

            for row in reader:
                if not row:
                    continue
                # If we're updating, remove the old student by old_id
                if update_mode and row[0] == old_id:
                    continue
                # If adding, check for duplicate ID
                if not update_mode and row[0] == student_id:
                    existing_student = row
                    continue
                updated_rows.append(row)

    if not update_mode and existing_student:
        existing_info = f"ID No.: {existing_student[0]}\nName: {existing_student[1]} {existing_student[2]}\nGender: {existing_student[3]}\nYear Level: {existing_student[4]}\nCollege: {existing_student[5]}\nProgram: {existing_student[6]}"
        confirm = messagebox.askyesno(
            "ID Already Exists",
            f"A student with ID No. {student_id} already exists.\n\n{existing_info}\n\nDo you want to override this student?"
        )
        if not confirm:
            return

    # Add the new/updated student row
    updated_rows.append(student_data)

    # Write back to CSV
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(updated_rows)

    # Refresh UI
    students = load_students()

    # Reset form
    id_no.delete(0, "end")
    id_no.insert(0, "Ex: 1234-5678")
    id_no.config(fg="gray", justify="center")

    last_name.delete(0, "end")
    first_name.delete(0, "end")
    gender_filter.set("Select")
    gender_filter.configure(foreground="gray")
    year_dropdown.set("Select")
    year_dropdown.configure(foreground="gray")

    college_filter.set("Select")
    college_filter.configure(foreground="gray")
    program_filter["state"] = "normal"
    program_filter.delete(0, "end")
    program_filter.insert(0, "Select College First")
    program_filter["state"] = "readonly"
    program_filter.configure(foreground="gray")

    saved_label = Label(root, bg="lightgray", width=30, text="Saved Successfully!", fg="green", font=("Arial", 10, "bold"))
    bind_reset_events()
    refresh_filter_dropdowns()
    refresh_students()
    refresh_table()
    update_summary()

    
    
def refresh_filter_dropdowns():
    
    global college_filter, college_filter_var, program_filter, program_filter_var

    colleges = load_colleges(return_list=True)
    college_filter_var.set("All Colleges")
    college_filter['values'] = colleges

    selected_college = college_filter_var.get()
    programs = load_programs(selected_college)
    program_filter_var.set("All Programs")
    program_filter['values'] = programs

def validate_student_data(data):
    errors = []

    if not re.match(r"^\d{4}-\d{4}$", data["id"]) or any(char.isalpha() for char in data["id"]):
        errors.append("• ID No. must be in the format XXXX-XXXX (e.g., 2024-1234) and contain only numbers.")

    for name_field in ["last_name", "first_name"]:
        value = data[name_field].title()
        if any(char.isdigit() for char in value):
            errors.append(f"• {name_field.replace('_', ' ').title()} must not contain numbers.")
        if not all(char.isalpha() or char in [' ', '-'] for char in value):
            errors.append(f"• {name_field.replace('_', ' ').title()} must contain only letters, spaces, or hyphens.")

    if data["gender"] == "Select":
        errors.append("• Please select a Gender.")

    if data["year"] == "Select":
        errors.append("• Please select a Year Level.")

    if data["college"] == "Select":
        errors.append("• Please select a College.")

    if data["program"] == "Select":
        errors.append("• Please select a Program.")

    return errors

def load_college_data(college_file="college.csv", program_file="program.csv"):
    college_data = {}

    # Load colleges
    try:
        with open(college_file, newline='', encoding="utf-8") as cfile:
            reader = csv.DictReader(cfile)
            for row in reader:
                college_name = row["College Name"].strip()
                college_code = row["College Code"].strip()
                if college_name and college_code:
                    college_data[college_name] = {
                        "code": college_code,
                        "programs": {}
                    }
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load colleges: {e}")
        return {}

    # Load programs
    try:
        with open(program_file, newline='', encoding="utf-8") as pfile:
            reader = csv.DictReader(pfile)
            for row in reader:
                college_name = row["College Name"].strip()
                program_name = row["Program Name"].strip()
                program_code = row["Program Code"].strip()
                if college_name in college_data and program_name and program_code:
                    college_data[college_name]["programs"][program_name] = program_code
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load programs: {e}")

    return college_data


def on_input_change(cancel_butt, *args):
    if search_var.get():
        cancel_butt.grid()
    else:
        cancel_butt.grid_remove()
    filter_students()



def clear_placeholder(event=None):
    if search_var.get() == "":
        icon_label.place_forget()
        text_label.place_forget()
    search_bar.focus_set()

def restore_placeholder(event=None):
    if search_var.get() == "":
        icon_label.place(x=x1 + -7, y=y1 + -3)
        text_label.place(x=x1 + 15, y=y1 + 1)

    points = [
        x1 + radius, y1, x2 - radius, y1,
        x2, y1, x2, y1 + radius, x2, y2 - radius,
        x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

def on_resize(event):
    global x1,y1
    search_frame.delete("all")
    margin = 6
    radius = 20
    canvas_width = search_frame.winfo_width()
    canvas_height = search_frame.winfo_height()

    x1 = margin
    y1 = margin
    x2 = canvas_width - margin
    y2 = canvas_height - margin

    

    icon_label.place(x=x1 + -7, y=y1 + -3)
    text_label.place(x=x1 + 15, y=y1 + 1)
    search_var.set("")
    cancel_butt.pack_forget()

def remove(event=None):
    root.focus_set()

def on_select(event):
    event.widget.configure(foreground="black")

    if event.widget == college_filter:
        selected_college = college_filter.get()
        
        college_code = selected_college.split(" - ")[0]

        program_names = []
        if os.path.exists(PROGRAM_FILE):
            with open(PROGRAM_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 3 and row[2] == college_code:  
                        program_names.append(f"{row[0]} - {row[1]}") 

        program_filter["values"] = program_names if program_names else ["No programs available"]
        program_filter.set("Select")

def update_summary():
    # Students
    total_students = 0
    if os.path.exists(STUDENT_CSV):
        with open(STUDENT_CSV, newline='', encoding='utf-8') as file:
            total_students = sum(1 for _ in csv.DictReader(file))

    # Colleges
    total_colleges = 0
    if os.path.exists(COLLEGE_CSV):
        with open(COLLEGE_CSV, newline='', encoding='utf-8') as file:
            total_colleges = sum(1 for _ in csv.DictReader(file))

    # Programs
    total_programs = 0
    if os.path.exists(PROGRAM_CSV):
        with open(PROGRAM_CSV, newline='', encoding='utf-8') as file:
            total_programs = sum(1 for _ in csv.DictReader(file))

    # Update labels
    total_colleges_label.config(text=f"Total Colleges: {total_colleges}")
    total_programs_label.config(text=f"Total Programs: {total_programs}")
    total_students_label.config(text=f"Total Students: {total_students}")

def delete_student(event=None):
    global students

    selected_item = student_tbl.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a student to delete.")
        return

    student_data = student_tbl.item(selected_item, "values")
    student_id = student_data[0]

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student ID {student_id}?")
    if not confirm:
        return

    # Update the CSV
    updated_rows = []
    with open("students.csv", "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if row and row[0] != student_id:
                updated_rows.append(row)

    with open("students.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(updated_rows)

    # Re-load students and refresh view
    students = load_students()
    refresh_students()         # Re-applies filters and updates table
    update_summary()           # Now accurately reflects the updated CSV

    messagebox.showinfo("Success", f"Student ID {student_id} has been deleted!")


def display_students():
    global current_page, students_per_page

    start_index = current_page * students_per_page
    end_index = start_index + students_per_page

    student_tbl.delete(*student_tbl.get_children())
    for student in display_students.current_students[start_index:end_index]:
        student_tbl.insert('', 'end', values=[
            student['Student ID'], student['Last Name'], student['First Name'], student['Gender'],
            student['College'], student['College Code'], student['Program'], student['Program Code'], student['Year']
        ])


# --- Initialize required attributes
display_students.original_students = []
display_students.current_students = []



def update_student():
    global students, current_page, total_pages, students_per_page, college_data
    college_data = load_college_data(CSV_COLLEGES, CSV_PROGRAMS)
    file_path = "students.csv"

    selected_item = student_tbl.focus()
    if not selected_item:
        messagebox.showerror("Error", "No student selected for update.")
        return

    student_data = student_tbl.item(selected_item, "values")
    old_id = student_data[0]  # ✅ Fixed: Get the old ID from the selected data

    id_var = tk.StringVar(value=student_data[0])
    lastname_var = tk.StringVar(value=student_data[1])
    firstname_var = tk.StringVar(value=student_data[2])
    gender_var = tk.StringVar(value=student_data[3])
    college_var = tk.StringVar(value=student_data[4])
    college_code_var = tk.StringVar(value=student_data[5])
    program_var = tk.StringVar(value=student_data[6])
    program_code_var = tk.StringVar(value=student_data[7])
    year_var = tk.StringVar(value=student_data[8])

    upgroot = Toplevel()
    upgroot.grab_set()
    upgroot.title("Update Student Data")
    upgroot.geometry("470x550+220+200")
    upgroot.config(bg='lightgrey')
    upgroot.resizable(False, False)

    def update_program_list(event=None):
        selected_college = college_var.get()
        if selected_college in college_data:
            programs = list(college_data[selected_college]["programs"].keys())
            if not programs:
                programs = ["N/A"]
                program_code_var.set("N/A")

            program_combo["values"] = programs
            college_code_var.set(college_data[selected_college]["code"])

            if program_var.get() not in programs:
                program_var.set(programs[0])
            program_code_var.set(college_data[selected_college]["programs"].get(program_var.get(), "N/A"))
        else:
            program_combo["values"] = []
            college_code_var.set("")
            program_code_var.set("")

    def save_update():
        new_id = id_var.get().strip()
        last_name = lastname_var.get().strip().title()
        first_name = firstname_var.get().strip().title()
        gender = gender_var.get()
        year = year_var.get()
        college = college_var.get()
        college_code = college_code_var.get()
        program = program_var.get()
        program_code = program_code_var.get()

        errors = []

        if not re.match(r"^\d{4}-\d{4}$", new_id):
            errors.append("• ID No. must be in the format YYYY-NNNN (e.g., xxxx-yyyy).")

        if not last_name or not first_name:
            errors.append("• First Name and Last Name cannot be empty.")
        if any(char.isdigit() for char in last_name):
            errors.append("• Last Name must not contain numbers.")
        if any(char.isdigit() for char in first_name):
            errors.append("• First Name must not contain numbers.")
        if gender not in ["Male", "Female"]:
            errors.append("• Please select a Gender.")
        if year not in ["1", "2", "3", "4"]:
            errors.append("• Please select a valid Year Level.")
        if college not in college_data:
            errors.append("• Please select a valid College.")
        if program != "N/A" and program not in college_data[college]["programs"]:
            errors.append("• Please select a valid Program.")

        # ✅ Check for duplicate only if new ID is different from old ID
        with open("students.csv", "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)
            for row in reader:
                if row and row[0] == new_id and new_id != old_id:
                    errors.append(f"• A student with ID {new_id} already exists.")
                    break

        if errors:
            messagebox.showerror("Form Error", "\n".join(errors))
            return

        confirm = messagebox.askyesno("Confirm Update", f"Update student ID {old_id} to {new_id}?")
        if not confirm:
            return

        updated_rows = []
        with open("students.csv", "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)
            for row in reader:
                if row and row[0] != old_id:
                    updated_rows.append(row)

        if program == "N/A":
            program_code = "N/A"

        updated_rows.append([
            new_id, last_name, first_name, gender,
            college, college_code, program, program_code, year
        ])

        with open("students.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(updated_rows)

        messagebox.showinfo("Success", "Student information updated!")
        refresh_table()
        upgroot.destroy()

    # UI Layout
    row_i = 0
    def row(label, widget):
        nonlocal row_i
        tk.Label(upgroot, text=label, font=('times', 17, 'bold'), bg="lightgrey").grid(row=row_i, column=0, padx=5, pady=5)
        widget.grid(row=row_i, column=1, padx=5, pady=5)
        row_i += 1

    row("Student ID", tk.Entry(upgroot, font=("times", 17), textvariable=id_var))
    row("Last Name", tk.Entry(upgroot, font=("times", 17), textvariable=lastname_var))
    row("First Name", tk.Entry(upgroot, font=("times", 17), textvariable=firstname_var))
    row("Gender", ttk.Combobox(upgroot, font=("times", 17), state="readonly", textvariable=gender_var, values=["Male", "Female"]))
    row("Year", ttk.Combobox(upgroot, font=("times", 17), state="readonly", textvariable=year_var, values=["1", "2", "3", "4"]))

    college_combo = ttk.Combobox(upgroot, font=("times", 17), state="readonly", textvariable=college_var, values=list(college_data.keys()))
    college_combo.bind("<<ComboboxSelected>>", update_program_list)
    row("College", college_combo)

    row("College Code", tk.Entry(upgroot, font=("times", 17), textvariable=college_code_var, state="readonly"))

    program_combo = ttk.Combobox(upgroot, font=("times", 17), state="readonly", textvariable=program_var)
    program_combo.bind("<<ComboboxSelected>>", lambda e: program_code_var.set(college_data[college_var.get()]["programs"].get(program_var.get(), "")))
    row("Program", program_combo)

    row("Program Code", tk.Entry(upgroot, font=("times", 17), textvariable=program_code_var, state="readonly"))

    tk.Button(upgroot, text="Update", command=save_update, font=("Arial", 13), width=18, bg="lightgrey").place(x=50, y=500)
    tk.Button(upgroot, text="Cancel", command=upgroot.destroy, font=("Arial", 13), width=18, bg="lightgrey").place(x=250, y=500)

    update_program_list()

def register_student():
    global students, current_page, total_pages, students_per_page, college_data
    college_data = load_college_data(CSV_COLLEGES, CSV_PROGRAMS)
    file_path = "students.csv"

    id_var = tk.StringVar()
    lastname_var = tk.StringVar()
    firstname_var = tk.StringVar()
    gender_var = tk.StringVar()
    college_var = tk.StringVar()
    college_code_var = tk.StringVar()
    program_var = tk.StringVar()
    program_code_var = tk.StringVar()
    year_var = tk.StringVar()

    regroot = Toplevel()
    regroot.grab_set()
    regroot.title("Register New Student")
    regroot.geometry("470x550+220+200")
    regroot.config(bg='lightgrey')
    regroot.resizable(False, False)

    def update_program_list(event=None):
        selected_college = college_var.get()
        if selected_college in college_data:
            programs = list(college_data[selected_college]["programs"].keys())
            if not programs:
                programs = ["N/A"]
                program_code_var.set("N/A")
            program_combo["values"] = programs
            college_code_var.set(college_data[selected_college]["code"])

            if program_var.get() not in programs:
                program_var.set(programs[0])
            program_code_var.set(college_data[selected_college]["programs"].get(program_var.get(), "N/A"))
        else:
            program_combo["values"] = []
            college_code_var.set("")
            program_code_var.set("")
        update_summary()
        refresh_filter_dropdowns()
        refresh_table()
        regroot.destroy()

    def save_register():
        new_id = id_var.get().strip()
        last_name = lastname_var.get().strip().title()
        first_name = firstname_var.get().strip().title()
        gender = gender_var.get()
        year = year_var.get()
        college = college_var.get()
        college_code = college_code_var.get()
        program = program_var.get()
        program_code = program_code_var.get()

        errors = []

        if not re.match(r"^\d{4}-\d{4}$", new_id):
            errors.append("• ID No. must be in the format YYYY-NNNN (e.g., xxxx-yyyy).")
        if not last_name or not first_name:
            errors.append("• First Name and Last Name cannot be empty.")
        if any(char.isdigit() for char in last_name):
            errors.append("• Last Name must not contain numbers.")
        if any(char.isdigit() for char in first_name):
            errors.append("• First Name must not contain numbers.")
        if gender not in ["Male", "Female"]:
            errors.append("• Please select a Gender.")
        if year not in ["1", "2", "3", "4"]:
            errors.append("• Please select a valid Year Level.")
        if college not in college_data:
            errors.append("• Please select a valid College.")
        if program != "N/A" and program not in college_data[college]["programs"]:
            errors.append("• Please select a valid Program.")

        # ✅ Check if ID already exists
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)
            for row in reader:
                if row and row[0] == new_id:
                    errors.append(f"• A student with ID {new_id} already exists.")
                    break

        if errors:
            messagebox.showerror("Form Error", "\n".join(errors))
            return

        confirm = messagebox.askyesno("Confirm Registration", f"Register student with ID {new_id}?")
        if not confirm:
            return

        if program == "N/A":
            program_code = "N/A"

        with open(file_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                new_id, last_name, first_name, gender,
                college, college_code, program, program_code, year
            ])

        messagebox.showinfo("Success", "New student registered successfully!")
        update_summary()
        refresh_filter_dropdowns()
        refresh_table()
        regroot.destroy()

    # UI Layout
    row_i = 0
    def row(label, widget):
        nonlocal row_i
        tk.Label(regroot, text=label, font=('times', 17, 'bold'), bg="lightgrey").grid(row=row_i, column=0, padx=5, pady=5)
        widget.grid(row=row_i, column=1, padx=5, pady=5)
        row_i += 1

    row("Student ID", tk.Entry(regroot, font=("times", 17), textvariable=id_var))
    row("Last Name", tk.Entry(regroot, font=("times", 17), textvariable=lastname_var))
    row("First Name", tk.Entry(regroot, font=("times", 17), textvariable=firstname_var))
    row("Gender", ttk.Combobox(regroot, font=("times", 17), state="readonly", textvariable=gender_var, values=["Male", "Female"]))
    row("Year", ttk.Combobox(regroot, font=("times", 17), state="readonly", textvariable=year_var, values=["1", "2", "3", "4"]))

    college_combo = ttk.Combobox(regroot, font=("times", 17), state="readonly", textvariable=college_var, values=list(college_data.keys()))
    college_combo.bind("<<ComboboxSelected>>", update_program_list)
    row("College", college_combo)

    row("College Code", tk.Entry(regroot, font=("times", 17), textvariable=college_code_var, state="readonly"))

    program_combo = ttk.Combobox(regroot, font=("times", 17), state="readonly", textvariable=program_var)
    program_combo.bind("<<ComboboxSelected>>", lambda e: program_code_var.set(college_data[college_var.get()]["programs"].get(program_var.get(), "")))
    row("Program", program_combo)

    row("Program Code", tk.Entry(regroot, font=("times", 17), textvariable=program_code_var, state="readonly"))

    tk.Button(regroot, text="Register", command=save_register, font=("Arial", 13), width=18, bg="lightgrey").place(x=50, y=500)
    tk.Button(regroot, text="Cancel", command=regroot.destroy, font=("Arial", 13), width=18, bg="lightgrey").place(x=250, y=500)

    update_program_list()
    update_summary()



COLLEGE_FILE = "colleges.csv"
college_names = {}

def load_colleges(return_list=False):

    global college_names
    college_names.clear()

    college_list = ["All Colleges"] if return_list else []

    file_path = CSV_COLLEGES if os.path.exists(CSV_COLLEGES) else COLLEGE_FILE

    if not os.path.exists(file_path):
        return college_list if return_list else None

    try:
        with open(file_path, newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file) if file_path == CSV_COLLEGES else csv.reader(file)

            for row in reader:
                if isinstance(row, dict):
                    # DictReader expected fields: "College Code", "College Name"
                    code = row.get("College Code", "").strip()
                    name = row.get("College Name", "").strip()
                else:
                    if len(row) != 2:
                        continue
                    code, name = row[0].strip(), row[1].strip()

                if code and name:
                    formatted = f"{code} - {name}"
                    college_names[formatted] = []
                    if return_list:
                        college_list.append(name)

    except Exception as e:
        messagebox.showerror("Load Error", f"Error loading colleges: {e}")
        print(f"Error loading colleges: {e}")

    return college_list if return_list else None


def remove_focus(event):
    global sorting
    widget = event.widget

    if isinstance(widget, (Entry, Button, ttk.Combobox, ttk.Treeview, Label, Canvas)):
        return

    tree.selection_remove(tree.selection())
    root.focus_set()
    
def on_root_resize(event):
    total_width = root.winfo_width()

    sidebar_width = max(220, min(270, int(total_width * 0.25)))

    root.columnconfigure(0, minsize=sidebar_width)

    side.config(width=sidebar_width)


def load_data():
    students = load_students()
    
    if not os.path.exists(CSV_STUDENTS):
        with open(CSV_STUDENTS, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Student ID", "Last Name", "First Name", "Gender", "College", "College Code", "Program", "Program Code", "Year"])
    else:
        with open(CSV_STUDENTS, "r") as file:
            reader = csv.reader(file)
            next(reader, None)  
            for row in reader:
                student_tbl.insert("", "end", values=row)

def update_csv_from_table():
    try:
        with open(CSV_STUDENTS, "r", newline="") as file:
            reader = csv.DictReader(file)
            all_students = list(reader)
    except FileNotFoundError:
        messagebox.showerror("File Error", f"The '{CSV_STUDENTS}' file was not found.")
        return

    students_dict = {student["Student ID"]: student for student in all_students}

    for row in student_tbl.get_children():
        values = student_tbl.item(row)['values']
        updated_student = {
            "Student ID": values[0],
            "Last Name": values[1],
            "First Name": values[2],
            "Gender": values[3],
            "College": values[4],
            "College Code": values[5],
            "Program": values[6],
            "Program Code": values[7],
            "Year": values[8]
        }
        students_dict[updated_student["Student ID"]] = updated_student

    with open(CSV_STUDENTS, "w", newline="") as file:
        fieldnames = ["Student ID", "Last Name", "First Name", "Gender", "College",
                      "College Code", "Program", "Program Code", "Year"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for student in sorted(students_dict.values(), key=lambda x: (x["Last Name"].lower(), x["First Name"].lower())):
            writer.writerow(student)

    for item in student_tbl.get_children():
        student_tbl.delete(item)
    load_data()

    messagebox.showinfo("Update Success", "Student records updated successfully.")

def load_programs(college):
    programs = ["All Programs"]
    seen = set()

    if os.path.exists(CSV_PROGRAMS):
        with open(CSV_PROGRAMS, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if college == "All Colleges" or row["College Name"] == college:
                    name = row["Program Name"]
                    if name not in seen:
                        programs.append(name)
                        seen.add(name)

    if os.path.exists(CSV_STUDENTS):
        with open(CSV_STUDENTS, newline="") as file:
            for row in csv.DictReader(file):
                if row["Program"] == "N/A" and "N/A" not in programs:
                    programs.append("N/A")
                    break

    return programs

def load_filtered_students(college_filter, program_filter, sort_option):
    students = []
    if os.path.exists(CSV_STUDENTS):
        with open(CSV_STUDENTS, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (college_filter == "All Colleges" or row["College"] == college_filter) and                    (program_filter == "All Programs" or row["Program"] == program_filter):
                    students.append(row)

    def sort_key(student):
        gender_priority = 0 if student["Gender"].lower() == "female" else 1
        year_priority_map = {"4": 1, "3": 2, "2": 3, "1": 4}
        year_priority = year_priority_map.get(student["Year"], 5)
        lname = student["Last Name"].lower()
        fname = student["First Name"].lower()

        if sort_option == "First Name A-Z":
            return (fname,)
        elif sort_option == "First Name Z-A":
            return (fname,)
        elif sort_option == "Last Name A-Z":
            return (lname,)
        elif sort_option == "Last Name Z-A":
            return(lname,)
        elif sort_option == "Gender":
            return (gender_priority, lname, fname)
        elif sort_option == "Year":
            return (year_priority, lname, fname)
        else: 
            return (lname,)

    reverse = sort_option in ["First Name Z-A", "Last Name Z-A"]
    students.sort(key=sort_key, reverse=reverse)
    return students
def show_all():
    for row in student_tbl.get_children():
        student_tbl.delete(row)
    load_data()


def exit_student():
    res = messagebox.askyesnocancel('Notification','Do you want to exit?')
    if(res == True):
        win.destroy()
    
    
COLLEGE_CSV = 'colleges.csv'
PROGRAM_CSV = 'programs.csv'
STUDENT_CSV = 'students.csv'

def read_csv(file_path):
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []

def write_csv(file_path, fieldnames, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

class CollegeManagerLogic:
    def __init__(self, college_file=COLLEGE_CSV, student_file=STUDENT_CSV):
        self.college_file = college_file
        self.student_file = student_file
        
    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())  # Clear table
        colleges = self.manager.get_all_colleges()
        for college in colleges:
            self.tree.insert('', 'end', values=(college["College Name"], college["College Code"], college["Programs"], college["Students"]))

    def get_colleges(self):
        return read_csv(self.college_file)

    def backup_csv(self, filename='colleges.csv'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        backup_filename = os.path.join(backup_dir, f'colleges_backup_{timestamp}.csv')
        shutil.copy(filename, backup_filename)

    def get_all_colleges(self):
        colleges = []
        try:
            with open(self.college_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    code = row['College Code'].strip()
                    colleges.append({
                        'College Name': row['College Name'].strip(),
                        'College Code': code,
                        'Programs': self.count_programs_by_college(code),
                        'Students': self.count_students_by_college(code)
                    })
        except FileNotFoundError:
            pass
        return colleges

    def count_programs_by_college(self, college_code):
        college_code = college_code.strip().lower()
        programs = read_csv(PROGRAM_CSV)
        return sum(1 for p in programs if p['College Code'].strip().lower() == college_code)

    def count_students_by_college(self, college_code):
        college_code = college_code.strip().lower()
        students = read_csv(STUDENT_CSV)
        return sum(1 for s in students if s['College Code'].strip().lower() == college_code)

    def add_college(self, name, code):
        name, code = name.strip(), code.strip()
        colleges = self.get_colleges()
        for c in colleges:
            if c['College Name'].strip().lower() == name.lower() or c['College Code'].strip().lower() == code.lower():
                raise ValueError("College with this name or code already exists.")
        colleges.append({'College Name': name, 'College Code': code})
        filtered = [{'College Name': c['College Name'], 'College Code': c['College Code']} for c in colleges]
        write_csv(self.college_file, ['College Name', 'College Code'], filtered)


    def edit_college(self, old_code, new_name, new_code):
        new_name, new_code = new_name.strip(), new_code.strip()
        colleges = self.get_colleges()
        if old_code != new_code and any(c['College Code'].strip().lower() == new_code.lower() for c in colleges):
            raise ValueError(f"A college with code '{new_code}' already exists.")
        found = False
        for c in colleges:
            if c['College Code'].strip().lower() == old_code.strip().lower():
                c['College Name'] = new_name
                c['College Code'] = new_code
                found = True
                break
        if not found:
            raise ValueError(f"College with code '{old_code}' not found.")
        filtered = [{'College Name': c['College Name'], 'College Code': c['College Code']} for c in colleges]
        write_csv(self.college_file, ['College Name', 'College Code'], filtered)


        if old_code != new_code:
            students = read_csv(self.student_file)
            updated = False
            for s in students:
                if s['College Code'].strip().lower() == old_code.strip().lower():
                    s['College Code'] = new_code
                    s['College'] = new_name
                    updated = True
            if updated and students:
                write_csv(self.student_file, students[0].keys(), students)
                    
    def update_college(self, old_name, old_code, new_name, new_code):
        colleges = read_csv(self.college_file)

        # Check for duplicate (only if name or code is changing)
        for college in colleges:
            if (college['College Name'] == new_name and college['College Code'] == new_code and 
                (new_name != old_name or new_code != old_code)):
                raise ValueError("A college with the same name and code already exists.")

        updated = False
        for college in colleges:
            if college['College Name'] == old_name and college['College Code'] == old_code:
                college['College Name'] = new_name
                college['College Code'] = new_code
                updated = True
                break

        if not updated:
            raise ValueError("College not found for update.")

        write_csv(self.college_file, ["College Name", "College Code"], colleges)

        # Update college name/code in programs and students
        self._update_college_name_in_programs(old_name, new_name)
        self._update_college_name_in_students(old_name, new_name)


    def _update_college_name_in_programs(self, old_name, new_name):
        programs = read_csv(PROGRAM_CSV)
        for program in programs:
            if program['College Name'] == old_name:
                program['College Name'] = new_name
        if programs:
            write_csv(PROGRAM_CSV, programs[0].keys(), programs)


    def _update_college_name_in_students(self, old_name, new_name):
        students = read_csv(self.student_file)
        for student in students:
            if student['College'] == old_name:
                student['College'] = new_name
        if students:
            write_csv(self.student_file, students[0].keys(), students)

    def delete_college(self, college_code):
        college_code = college_code.strip()
        colleges = self.get_colleges()
        college = next((c for c in colleges if c['College Code'].strip() == college_code), None)
        if not college:
            raise ValueError("College not found.")
        
        # Remove the college from the college list
        updated_colleges = [c for c in colleges if c['College Code'].strip() != college_code]
        write_csv(self.college_file, ['College Name', 'College Code'], updated_colleges)

        # Update students
        students = read_csv(self.student_file)
        updated_students = False
        for s in students:
            if s.get('College Code', '').strip() == college_code:
                s['College'] = 'N/A'
                s['College Code'] = 'N/A'
                updated_students = True
        if updated_students and students:
            write_csv(self.student_file, students[0].keys(), students)

        # ✅ Update programs
        programs = read_csv(PROGRAM_CSV)
        updated_programs = False
        for p in programs:
            if p.get('College Code', '').strip() == college_code:
                p['College Name'] = 'N/A'
                p['College Code'] = 'N/A'
                updated_programs = True
        if updated_programs and programs:
            write_csv(PROGRAM_CSV, programs[0].keys(), programs)


class CollegeManagerWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("College Manager")
        self.geometry("900x500") 
        self.logic = CollegeManagerLogic()
        self.create_widgets()
        self.load_colleges()
    
    def load_colleges(self):
        self.colleges = self.logic.get_all_colleges()
        self.update_table()
        
    def create_widgets(self):
        # Search Bar at the top, centered
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        
        self.search_var.trace("w", lambda *args: self.update_table())

        # Filter Options
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Sort by:").grid(row=0, column=0, padx=5)
        self.sort_option = tk.StringVar(value="College Name Asc")
        sort_options = [
            "College Name Asc", "College Name Desc",
            "College Code Asc", "College Code Desc",
            "Programs Count Asc", "Programs Count Desc",
            "Students Count Asc", "Students Count Desc"
        ]
        self.sort_menu = ttk.Combobox(filter_frame, textvariable=self.sort_option, values=sort_options, state="readonly")
        self.sort_menu.grid(row=0, column=1, padx=5)
        self.sort_menu.bind("<<ComboboxSelected>>", lambda e: self.update_table())

        # Table for displaying colleges
        self.tree = ttk.Treeview(self, columns=("College Name", "College Code", "Programs", "Students"), show="headings")
        self.tree.heading("College Name", text="College Name")
        self.tree.heading("College Code", text="College Code")
        self.tree.heading("Programs", text="# of Programs")
        self.tree.heading("Students", text="# of Students")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
            # Summary Frame Below Table
        self.summary_frame = tk.Frame(self)
        self.summary_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.total_colleges_label = tk.Label(self.summary_frame, text="Total Colleges: 0")
        self.total_colleges_label.pack(side=tk.LEFT, padx=10)

        self.total_programs_label = tk.Label(self.summary_frame, text="Total Programs: 0")
        self.total_programs_label.pack(side=tk.LEFT, padx=10)

        self.total_students_label = tk.Label(self.summary_frame, text="Total Students: 0")
        self.total_students_label.pack(side=tk.LEFT, padx=10)


        # Buttons at the bottom
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10, fill=tk.X)

        tk.Button(button_frame, text="Add College", command=self.add_college_popup).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update College", command=self.edit_college_popup).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete College", command=self.delete_college).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def delete_college(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a college to delete.")
            return

        try:
            college_code = self.tree.item(selected[0])['values'][1]
        except (IndexError, KeyError, TypeError):
            messagebox.showerror("Error", "Unable to retrieve college code.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete college '{college_code}'?")
            
        if not confirm:
            return

        try:
            self.logic.delete_college(college_code)
            self.load_colleges()  

            messagebox.showinfo("Deleted", "College deleted successfully. Students' college info updated to 'N/A'.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        refresh_students()
        update_summary()
        refresh_filter_dropdowns()

    def edit_college_popup(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select College", "Please select a college to edit.")
            return

        item = self.tree.item(selected_item)
        original_name = item['values'][0]
        original_code = item['values'][1]

        popup = tk.Toplevel(self)
        popup.title("Edit College")
        popup.geometry("400x200")

        tk.Label(popup, text="College Name:").pack(pady=5)
        name_entry = tk.Entry(popup)
        name_entry.insert(0, original_name)
        name_entry.pack(pady=5)

        tk.Label(popup, text="College Code:").pack(pady=5)
        code_entry = tk.Entry(popup)
        code_entry.insert(0, original_code)
        code_entry.pack(pady=5)

        def save():
            new_name = name_entry.get().strip()
            new_code = code_entry.get().strip()

            if not new_name or not new_code:
                messagebox.showwarning("Validation Error", "All fields must be filled.")
                return

            if not new_name.isalpha():
                messagebox.showwarning("Validation Error", "College name must contain only letters (A-Z or a-z).")
                return

            if not new_code.isalpha():
                messagebox.showwarning("Validation Error", "College code must contain only letters (A-Z or a-z).")
                return

            try:
                self.logic.update_college(original_name, original_code, new_name, new_code)
                self.load_colleges()
                messagebox.showinfo("Success", "College updated successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        save_btn = tk.Button(popup, text="Save", command=save)
        save_btn.pack(side='left', padx=10, pady=10)

        close_btn = tk.Button(popup, text="Close", command=popup.destroy)
        close_btn.pack(side='right', padx=10, pady=10)


    def update_table(self):
        search_query = self.search_var.get().lower()
        sort_key = self.sort_option.get()

        filtered = []
        for college in self.colleges:
            if (search_query in college['College Name'].lower() or
                search_query in college['College Code'].lower()):
                program_count = self.logic.count_programs_by_college(college['College Code'])
                student_count = self.logic.count_students_by_college(college['College Code'])
                filtered.append({
                    **college,
                    'program_count': program_count,
                    'student_count': student_count
                })

        if sort_key == "College Name Asc":
            filtered.sort(key=lambda x: x['College Name'].lower())
        elif sort_key == "College Name Desc":
            filtered.sort(key=lambda x: x['College Name'].lower(), reverse=True)
        elif sort_key == "College Code Asc":
            filtered.sort(key=lambda x: x['College Code'].lower())
        elif sort_key == "College Code Desc":
            filtered.sort(key=lambda x: x['College Code'].lower(), reverse=True)
        elif sort_key == "Programs Count Asc":
            filtered.sort(key=lambda x: x['program_count'])
        elif sort_key == "Programs Count Desc":
            filtered.sort(key=lambda x: x['program_count'], reverse=True)
        elif sort_key == "Students Count Asc":
            filtered.sort(key=lambda x: x['student_count'])
        elif sort_key == "Students Count Desc":
            filtered.sort(key=lambda x: x['student_count'], reverse=True)
            
        total_colleges = len(filtered)
        total_programs = sum(college['program_count'] for college in filtered)
        total_students = sum(college['student_count'] for college in filtered)

        self.total_colleges_label.config(text=f"Total Colleges: {total_colleges}")
        self.total_programs_label.config(text=f"Total Programs: {total_programs}")
        self.total_students_label.config(text=f"Total Students: {total_students}")


        # Clear and reload table
        for row in self.tree.get_children():
            self.tree.delete(row)
        for college in filtered:
            self.tree.insert("", tk.END, values=(
                college['College Name'],
                college['College Code'],
                college['program_count'],
                college['student_count']
            ))
        refresh_filter_dropdowns()
        refresh_students()
        update_summary()
        
    def add_college_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add College")
        popup.geometry("400x200")

        tk.Label(popup, text="College Name:").pack(pady=5)
        name_entry = tk.Entry(popup)
        name_entry.pack(pady=5)

        tk.Label(popup, text="College Code:").pack(pady=5)
        code_entry = tk.Entry(popup)
        code_entry.pack(pady=5)

        def save():
            name = name_entry.get().strip()
            code = code_entry.get().strip()

            if not name or not code:
                messagebox.showwarning("Validation Error", "All fields must be filled.")
                return

            if not name.isalpha():
                messagebox.showwarning("Validation Error", "College name must contain only letters (A-Z or a-z).")
                return

            if not code.isalpha():
                messagebox.showwarning("Validation Error", "College code must contain only letters (A-Z or a-z).")
                return

            try:
                self.logic.add_college(name, code)
                self.load_colleges()
                messagebox.showinfo("Success", "College added successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        save_btn = tk.Button(popup, text="Save", command=save)
        save_btn.pack(side='left', padx=10, pady=10)

        close_btn = tk.Button(popup, text="Close", command=popup.destroy)
        close_btn.pack(side='right', padx=10, pady=10)
        refresh_filter_dropdowns()
        refresh_students()
        update_summary()



class ProgramManagerLogic:
    def __init__(self):
        self.programs = []
        self.colleges = []
        self.students = []
        self.load_data()

    def load_data(self):
        self.programs = []
        self.colleges = []
        self.students = []

        # Load colleges
        try:
            with open(COLLEGE_CSV, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.colleges.append(row)
        except FileNotFoundError:
            pass

        # Load programs
        try:
            with open(PROGRAM_CSV, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.programs.append(row)
        except FileNotFoundError:
            pass

        # Load students
        try:
            with open(STUDENT_CSV, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.students.append(row)
        except FileNotFoundError:
            pass

    def save_programs(self):
        with open(PROGRAM_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Program Name', 'Program Code', 'College Name', 'College Code']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in self.programs:
                writer.writerow(p)

    def get_programs(self, filter_text=""):
        # Returns list of program dicts filtered by program name, code or college name
        filter_text = filter_text.lower()
        filtered = []
        for p in self.programs:
            if (filter_text in p['Program Name'].lower() or
                filter_text in p['Program Code'].lower() or
                filter_text in p['College Name'].lower()):
                filtered.append(p)
        filtered.sort(key=lambda p: p['Program Name'].lower())
        
        return filtered

    def get_college_names(self):
        return [c['College Name'] for c in self.colleges]

    def count_students_in_program(self, program_code):
        count = 0
        for s in self.students:
            if s.get('Program Code', '') == program_code:
                count += 1
        return count

    def total_students_in_programs(self):
        # Sum of students assigned to any program (Program Code != '')
        count = 0
        for s in self.students:
            if s.get('Program Code', '').strip() != '':
                count += 1
        return count

    def total_programs(self):
        return len(self.programs)

    def is_duplicate_program(self, program_name, program_code, exclude_index=None):
        for i, p in enumerate(self.programs):
            if exclude_index is not None and i == exclude_index:
                continue
            if p['Program Name'].lower() == program_name.lower() or p['Program Code'].lower() == program_code.lower():
                return True
        return False

    def add_program(self, college_name, program_name, program_code):
        # Validate inputs
        if not college_name or not program_name or not program_code:
            return False, "All fields must be filled."
        # Check college exists
        college = next((c for c in self.colleges if c['College Name'] == college_name), None)
        if not college:
            return False, "Selected college does not exist."
        # Check duplicates
        if self.is_duplicate_program(program_name, program_code):
            return False, "Program name or code already exists."

        new_program = {
            'Program Name': program_name.strip(),
            'Program Code': program_code.strip(),
            'College Name': college_name,
            'College Code': college['College Code']
        }
        self.programs.append(new_program)
        self.save_programs()
        refresh_filter_dropdowns()
        refresh_students()      
        update_summary()           

        return True, "Program added successfully."

    def update_program(self, index, college_name, program_name, program_code):
        if index < 0 or index >= len(self.programs):
            return False, "Invalid program selected."
        if not college_name or not program_name or not program_code:
            return False, "All fields must be filled."
        college = next((c for c in self.colleges if c['College Name'] == college_name), None)
        if not college:
            return False, "Selected college does not exist."
        if self.is_duplicate_program(program_name, program_code, exclude_index=index):
            return False, "Program name or code already exists."

        old_program = self.programs[index]
        old_program_code = old_program['Program Code']
        self.programs[index] = {
            'Program Name': program_name.strip(),
            'Program Code': program_code.strip(),
            'College Name': college_name,
            'College Code': college['College Code']
        }
        self.save_programs()

        if old_program_code != program_code.strip():
            for s in self.students:
                if s.get('Program Code', '') == old_program_code:
                    s['Program Code'] = program_code.strip()
            self.save_students()
        
        refresh_filter_dropdowns()
        refresh_students()         
        update_summary()           
        return True, "Program updated successfully."

    def save_students(self):
        if not self.students:
            return
        with open(STUDENT_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(self.students[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for s in self.students:
                writer.writerow(s)

    def delete_program(self, index):
        if index < 0 or index >= len(self.programs):
            return False, "Invalid program selected."

        program_to_delete = self.programs[index]
        program_code = program_to_delete['Program Code']

        # Remove program from programs list
        self.programs.pop(index)
        self.save_programs()

        # For students assigned to this program, set Program and Program Code to 'N/A'
        for s in self.students:
            if s.get('Program Code', '') == program_code:
                s['Program'] = 'N/A'
                s['Program Code'] = 'N/A'
        self.save_students()
        refresh_filter_dropdowns()
        refresh_students()      
        update_summary()           
        return True, "Program deleted successfully."
    
class ProgramManagerWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Program Manager")
        self.geometry("900x500")
        self.resizable(False, False)

        self.logic = ProgramManagerLogic()

        # Search Frame
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.update_table())
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var)
        self.clear_button = tk.Button(self.search_frame, text="Clear", command=lambda: self.search_var.set(""))
        self.clear_button.pack(side=tk.LEFT, padx=5)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.filter_frame = tk.Frame(self)
        self.filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(self.filter_frame, text="Sort by:").pack(side=tk.LEFT)
        self.sort_option = tk.StringVar(value="Program Name Asc")
        sort_choices = [
            "Program Name Asc", "Program Name Desc",
            "Program Code Asc", "Program Code Desc",
            "College Name Asc", "College Name Desc"
        ]
        self.sort_menu = ttk.Combobox(self.filter_frame, textvariable=self.sort_option, values=sort_choices, state="readonly")
        self.sort_menu.pack(side=tk.LEFT, padx=5)
        self.sort_menu.bind("<<ComboboxSelected>>", lambda e: self.update_table())

        tk.Label(self.filter_frame, text="Filter by Type:").pack(side=tk.LEFT, padx=(20, 5))
        self.type_filter_var = tk.StringVar(value="All")
        type_choices = ["All", "Bachelor of Science", "Technology", "Masteral"]
        self.type_menu = ttk.Combobox(self.filter_frame, textvariable=self.type_filter_var, values=type_choices, state="readonly")
        self.type_menu.pack(side=tk.LEFT)
        self.type_menu.bind("<<ComboboxSelected>>", lambda e: self.update_table())

        # Table Frame
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        columns = ("Program Name", "Program Code", "College Name", "Students")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200 if col != "Students" else 100, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons Frame
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(fill=tk.X, pady=5, padx=10)

        self.add_button = tk.Button(self.buttons_frame, text="Add", width=12, command=self.open_add_popup)
        self.add_button.pack(side=tk.LEFT, padx=5)
        self.update_button = tk.Button(self.buttons_frame, text="Update", width=12, command=self.open_update_popup)
        self.update_button.pack(side=tk.LEFT, padx=5)
        self.delete_button = tk.Button(self.buttons_frame, text="Delete", width=12, command=self.delete_program)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        self.close_button = tk.Button(self.buttons_frame, text="Close", width=12, command=self.destroy)
        self.close_button.pack(side=tk.RIGHT, padx=5)

        # Info Frame (Totals)
        self.info_frame = tk.Frame(self)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        self.total_programs_label = tk.Label(self.info_frame, text="Total Programs: 0")
        self.total_programs_label.pack(side=tk.LEFT)
        self.total_students_label = tk.Label(self.info_frame, text="Total Students: 0")
        self.total_students_label.pack(side=tk.RIGHT)

        self.update_table()

    def update_table(self):
        filter_text = self.search_var.get().lower()
        sort_by = self.sort_option.get()
        type_filter = self.type_filter_var.get()

        programs = self.logic.get_programs(filter_text)

        # Filter by Program Type
        if type_filter != "All":
            if type_filter == "Bachelor of Science":
                programs = [p for p in programs if "bachelor" in p['Program Name'].lower()]
            elif type_filter == "Technology":
                programs = [p for p in programs if "technology" in p['Program Name'].lower()]
            elif type_filter == "Masteral":
                programs = [p for p in programs if "master" in p['Program Name'].lower()]

        # Sort
        reverse = "Desc" in sort_by
        if "Program Name" in sort_by:
            programs.sort(key=lambda p: p['Program Name'].lower(), reverse=reverse)
        elif "Program Code" in sort_by:
            programs.sort(key=lambda p: p['Program Code'].lower(), reverse=reverse)
        elif "College Name" in sort_by:
            programs.sort(key=lambda p: p['College Name'].lower(), reverse=reverse)

        # Update Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, p in enumerate(programs):
            count_students = self.logic.count_students_in_program(p['Program Code'])
            self.tree.insert('', 'end', iid=i, values=(
                p['Program Name'],
                p['Program Code'],
                p['College Name'],
                count_students
            ))

        self.total_programs_label.config(text=f"Total Programs: {len(programs)}")
        total_students = self.logic.total_students_in_programs()
        self.total_students_label.config(text=f"Total Students: {total_students}")


        self.total_programs_label.config(text=f"Total Programs: {len(programs)}")
        total_students = self.logic.total_students_in_programs()
        self.total_students_label.config(text=f"Total Students: {total_students}")

    def open_add_popup(self):
        AddOrUpdateProgramPopup(self, self.logic, None, self.update_table)

    def open_update_popup(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a program to update.")
            return
        index = int(selected[0])
        AddOrUpdateProgramPopup(self, self.logic, index, self.update_table)

    def delete_program(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a program to delete.")
            return
        index = int(selected[0])
        program = self.logic.programs[index]
        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete the program '{program['Program Name']}'?")
        if not confirm:
            return
        success, msg = self.logic.delete_program(index)
        if success:
            messagebox.showinfo("Deleted", msg)
            self.update_table()
        else:
            messagebox.showerror("Error", msg)
        refresh_students()
        update_summary()
        refresh_filter_dropdowns()


class AddOrUpdateProgramPopup(tk.Toplevel):
    def __init__(self, master, logic: ProgramManagerLogic, program_index, refresh_callback):
        super().__init__(master)
        self.logic = logic
        self.program_index = program_index  # None if adding new
        self.refresh_callback = refresh_callback

        self.title("Add Program" if program_index is None else "Update Program")
        self.geometry("450x300")
        self.resizable(False, False)

        # College selection (dropdown)
        tk.Label(self, text="Select College:").pack(anchor=tk.W, padx=20, pady=(20, 5))
        self.college_var = tk.StringVar()
        self.college_filter = ttk.Combobox(self, textvariable=self.college_var, state="readonly")
        self.college_filter['values'] = self.logic.get_college_names()
        self.college_filter.pack(fill=tk.X, padx=20)

        # Program Name
        tk.Label(self, text="Program Name:").pack(anchor=tk.W, padx=20, pady=(15, 5))
        self.program_name_var = tk.StringVar()
        self.program_name_entry = tk.Entry(self, textvariable=self.program_name_var)
        self.program_name_entry.pack(fill=tk.X, padx=20)

        # Program Code
        tk.Label(self, text="Program Code:").pack(anchor=tk.W, padx=20, pady=(15, 5))
        self.program_code_var = tk.StringVar()
        self.program_code_entry = tk.Entry(self, textvariable=self.program_code_var)
        self.program_code_entry.pack(fill=tk.X, padx=20)

        # Buttons frame
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(fill=tk.X, pady=20, padx=20)

        self.save_button = tk.Button(self.buttons_frame, text="Save", width=12, command=self.save_program)
        self.save_button.pack(side=tk.LEFT, padx=(0,10))
        self.close_button = tk.Button(self.buttons_frame, text="Close", width=12, command=self.destroy)
        self.close_button.pack(side=tk.RIGHT)

        # If updating, populate fields
        if program_index is not None:
            program = self.logic.programs[program_index]
            self.college_var.set(program['College Name'])
            self.program_name_var.set(program['Program Name'])
            self.program_code_var.set(program['Program Code'])
    
        if program_index is not None and program['College Name'] not in self.college_filter['values']:
            self.college_filter['values'] = (*self.college_filter['values'], program['College Name'])


    def save_program(self):
        college_name = self.college_var.get()
        program_name = self.program_name_var.get().strip()
        program_code = self.program_code_var.get().strip()

        if self.program_index is None:
            # Add new
            success, msg = self.logic.add_program(college_name, program_name, program_code)
        else:
            # Update existing
            success, msg = self.logic.update_program(self.program_index, college_name, program_name, program_code)

        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

    

win = tk.Tk()
win.geometry("1350x700+0+0")
win.title("Student Management System")
win.configure(bg="#F3EBDF")

def open_college_manager():
    CollegeManagerWindow(win)  # open college manager window

def open_program_manager():
    ProgramManagerWindow(win)  # open program manager window

# Your buttons
college_btn = tk.Button(
    win,
    text="College",
    font=('Arial', 15, 'bold'),
    fg="#F3EBDF",
    bg='#6A1314',
    activebackground='blue',
    relief=tk.GROOVE,
    activeforeground='white',
    command=open_college_manager
)
college_btn.place(x=50, y=650, width=150, height=40)

tk.Button(
    win,
    text="Program",
    font=('Arial', 15, 'bold'),
    fg="#F3EBDF",
    bg='#6A1314',
    activebackground='blue',
    relief=tk.GROOVE,
    activeforeground='white',
    command=open_program_manager
).place(x=320, y=650, width=150, height=40)

def load_students():
    students = []
    if os.path.exists("students.csv"):
        with open("students.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                students.append(row)
    return students

def refresh_students():
    global students
    student_tbl.delete(*student_tbl.get_children())

    college_filter = college_filter_var.get()
    program_filter = program_filter_var.get()
    gender_filter = gender_filter_var.get()
    sort_option = sort_by_var.get()


    students = load_students()

    if college_filter != "All Colleges":
        students = [s for s in students if s["College"] == college_filter]
    if program_filter != "All Programs":
        students = [s for s in students if s["Program"] == program_filter]
    if gender_filter != "All Genders":
        students = [s for s in students if s["Gender"] == gender_filter]



    reverse = "Desc" in sort_option
    if "First Name" in sort_option:
        students.sort(key=lambda s: s["First Name"].lower(), reverse=reverse)
    elif "Last Name" in sort_option:
        students.sort(key=lambda s: s["Last Name"].lower(), reverse=reverse)
    elif "Year" in sort_option:
        students.sort(key=lambda s: int(s["Year"]), reverse=reverse)
    elif "Gender" in sort_option:
        students.sort(key=lambda s: s["Gender"].lower(), reverse=reverse)

    for s in students:
        student_tbl.insert('', 'end', values=[
            s['Student ID'], s['Last Name'], s['First Name'], s['Gender'],
            s['College'], s['College Code'], s['Program'], s['Program Code'], s['Year']
        ])

search_var = tk.StringVar()
search_frame = tk.LabelFrame(win, bd=3, relief=tk.SUNKEN, bg="#F3EBDF")
search_frame.place(x=665, y=10)

search_entry = tk.Entry(search_frame, textvariable=search_var, bd=0, relief=tk.FLAT, font=("Arial", 20), width=40)
search_entry.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
search_entry.bind("<KeyRelease>", lambda event: search_students())

try:
    searchicon = tk.PhotoImage(file="searchicon.png")
    search_label = tk.Label(search_frame, image=searchicon, bg="lightgrey")
    search_label.pack(side=tk.RIGHT)
except Exception:
    search_label = tk.Label(search_frame, text="🔍", font=("Arial", 18), bg="lightgrey")
    search_label.pack(side=tk.RIGHT)
    
register_btn = tk.Button(
    text="Register Student",
    width=40,
    font=('Arial', 18, 'bold'),
    fg="#F3EBDF",
    bg='#6A1314',
    activebackground='blue',
    relief=tk.GROOVE,
    activeforeground='white',
    command=register_student  # reference the function WITHOUT parentheses
)
register_btn.place(x=30, y=10, width=250, height=40)

refreshicon=tk.PhotoImage(file="refreshicon.png")
show_btn = tk.Button(win,text = "  Refresh  ",compound=tk.RIGHT,image=refreshicon,width=230,height=40,font=('Arial',18,'bold'),fg="#F3EBDF",bd=3,bg='#6A1314',activebackground='blue',relief=tk.GROOVE,activeforeground='white',command=show_all)
show_btn.place(x=350,y=10,width=250,height=40)

update_btn = tk.Button(
    win,
    text="Update",
    width=12,
    font=('Arial', 15, 'bold'),
    fg="#F3EBDF",
    bg='#6A1314',
    activebackground='blue',
    relief=tk.GROOVE,
    activeforeground='white',
    command=update_student  # ✅ No lambda, no arguments
)

update_btn.place(x=600, y=650, width=150, height=40)


delete_btn = tk.Button(win,text = "Delete",width=12,font=('Arial',15,'bold'),fg="#F3EBDF",bg='#6A1314',activebackground='blue',relief=tk.GROOVE,activeforeground='white',command=delete_student)
delete_btn.place(x=870,y=650,width=150,height=40)

exit_btn = tk.Button(text = "Exit",width=15,font=('Arial',18,'bold'),fg="#F3EBDF",bg='#6A1314',activebackground='blue',relief=tk.GROOVE,activeforeground='white',command=exit_student)
exit_btn.place(x=1150,y=650,width=150,height=40)

# --- Student Table Frame ---
tree_frame = tk.Frame(win, bd=3, relief=tk.GROOVE)
tree_frame.place(x=50, y=150, width=1250, height=470)  # Table area

columns = (
    "Student ID", "Last Name", "First Name", "Gender",
    "College", "College Code", "Program", "Program Code", "Year"
)

student_tbl = ttk.Treeview(tree_frame, columns=columns, show='headings')
for col in columns:
    student_tbl.heading(col, text=col)
    student_tbl.column(col, width=120)
student_tbl.pack(fill=tk.BOTH, expand=True)

# --- Summary Frame (below table) ---
summary_frame = tk.Frame(win, bg="#F3EBDF")
summary_frame.place(x=50, y=625, width=1250, height=15)  # Position directly below the 470px tall table

total_colleges_label = tk.Label(summary_frame, text="Total Colleges: 0", font=("Arial", 11), bg="#F3EBDF", fg="black")
total_colleges_label.pack(side=tk.LEFT, padx=20)

total_programs_label = tk.Label(summary_frame, text="Total Programs: 0", font=("Arial", 11), bg="#F3EBDF", fg="black")
total_programs_label.pack(side=tk.LEFT, padx=20)

total_students_label = tk.Label(summary_frame, text="Total Students: 0", font=("Arial", 11), bg="#F3EBDF", fg="black")
total_students_label.pack(side=tk.LEFT, padx=20)


def search_students(event=None):
    query = search_var.get().strip().lower()
    college = college_filter_var.get()
    program = program_filter_var.get()
    sort_option = sort_by_var.get()

    students = load_filtered_students(college, program, sort_option)

    student_tbl.delete(*student_tbl.get_children())

    for student in students:
        if not query or any(query in str(value).lower() for value in student.values()):
            student_tbl.insert('', 'end', values=[
                student['Student ID'], student['Last Name'], student['First Name'], student['Gender'],
                student['College'], student['College Code'], student['Program'], student['Program Code'], student['Year']
            ])
            
# Filter Frame (must be defined FIRST)
filter_frame = tk.LabelFrame(win, text="", font=("Arial", 18, "bold"), bg="#F3EBDF", bd=0)
filter_frame.place(x=150, y=70)

# Vars
college_filter_var = tk.StringVar(value="All Colleges")
program_filter_var = tk.StringVar(value="All Programs")
gender_filter_var = tk.StringVar(value="All Genders")
sort_by_var = tk.StringVar(value="First Name Asc")

# College Filter Label & Dropdown
tk.Label(filter_frame, text="Filter by College:", font=("Arial", 10), bg="#F3EBDF").grid(row=0, column=2, padx=5, sticky="w")
college_filter = ttk.Combobox(filter_frame, textvariable=college_filter_var, font=("Arial", 12), state="readonly", width=15)
college_list = load_colleges(return_list=True)
college_filter['values'] = ["All Colleges"] + college_list
college_filter.current(0)
college_filter.grid(row=0, column=3, padx=5, pady=2)

# Program Filter Label & Dropdown
tk.Label(filter_frame, text="Filter by Program:", font=("Arial", 10), bg="#F3EBDF").grid(row=0, column=4, padx=5, sticky="w")
program_filter = ttk.Combobox(filter_frame, textvariable=program_filter_var, font=("Arial", 12), state="readonly", width=15)
program_filter['values'] = load_programs("All Colleges")
program_filter.current(0)
program_filter.grid(row=0, column=5, padx=5, pady=2)

tk.Label(filter_frame, text="Filter by Gender:", font=("Arial", 10), bg="#F3EBDF").grid(row=0, column=6, padx=5, sticky="w")
gender_filter = ttk.Combobox(filter_frame, textvariable=gender_filter_var, font=("Arial", 12), state="readonly", width=15)
gender_filter['values'] = ["All Genders", "Male", "Female"]
gender_filter.current(0)
gender_filter.grid(row=0, column=7, padx=5, pady=2)

# When college changes, update program list
def update_program_filter(event):
    selected_college = college_filter_var.get()
    program_filter['values'] = load_programs(selected_college)
    program_filter.current(0)

college_filter.bind("<<ComboboxSelected>>", update_program_filter)

# Sort Label & Dropdown
tk.Label(filter_frame, text="Sort by:", font=("Arial", 10), bg="#F3EBDF").grid(row=0, column=0, padx=5, sticky="w")
sort_choices = [
    "First Name Asc", "First Name Desc",
    "Last Name Asc", "Last Name Desc",
    "Year Asc", "Year Desc"
]
sort_dropdown = ttk.Combobox(filter_frame, textvariable=sort_by_var, values=sort_choices, state="readonly", width=15)
sort_dropdown.current(0)
sort_dropdown.grid(row=0, column=1, padx=5, pady=(0, 1))

# Apply Button
apply_filter_btn = tk.Button(filter_frame, text="Apply Filters", command=refresh_students, font=("Arial", 11), bg="#6A1314", fg="white")
apply_filter_btn.grid(row=1, column=4, pady=(10, 0), sticky="e")

update_summary()
refresh_students()
win.mainloop()



