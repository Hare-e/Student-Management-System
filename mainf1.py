
import tkinter as tk
from tkinter import font, messagebox, ttk, Toplevel
from tkinter import filedialog
import csv
import os
import re

CSV_STUDENTS = "students.csv"
CSV_COLLEGES = "colleges.csv"
CSV_PROGRAMS = "programs.csv"

def save_to_csv(data):
    with open(CSV_STUDENTS, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(data)

def load_data():
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
        with open(CSV_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)
            all_students = list(reader)
    except FileNotFoundError:
        messagebox.showerror("File Error", f"The '{CSV_FILE}' file was not found.")
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

    with open(CSV_FILE, "w", newline="") as file:
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

def delete_student():
    selected_item = student_tbl.selection()
    if not selected_item:
        messagebox.showwarning("Delete Error", "Please select a student record to delete.")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected student(s)?")
    if not confirm:
        return

    try:
        with open(CSV_STUDENTS, "r", newline="") as file:
            reader = csv.DictReader(file)
            all_students = list(reader)

        students_dict = {student["Student ID"]: student for student in all_students}

        for item in selected_item:
            student_id = student_tbl.item(item)['values'][0]
            if student_id in students_dict:
                del students_dict[student_id]
            student_tbl.delete(item)

        with open(CSV_STUDENTS, "w", newline="") as file:
            fieldnames = ["Student ID", "Last Name", "First Name", "Gender", "College",
                          "College Code", "Program", "Program Code", "Year"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for student in sorted(students_dict.values(), key=lambda x: (x["Last Name"].lower(), x["First Name"].lower())):
                writer.writerow(student)

        messagebox.showinfo("Delete Success", "Selected student record(s) deleted successfully.")
        load_data()

    except FileNotFoundError:
        messagebox.showerror("File Error", f"The '{CSV_STUDENTS}' file was not found.")

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


def load_colleges():
    colleges = ["All Colleges"]
    if os.path.exists(CSV_COLLEGES):
        with open(CSV_COLLEGES, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                colleges.append(row["College Name"])
    return colleges

def load_programs(college):
    programs = ["All Programs"]
    if os.path.exists(CSV_PROGRAMS):
        with open(CSV_PROGRAMS, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if college == "All Colleges" or row["College Name"] == college:
                    programs.append(row["Program Name"])
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
    
def register_student_btn():

    def validate_student_id(student_id):
        
        return bool(re.match(r"^\d{4}-\d{4}$", student_id))

    def validate_name(name):
        
        return bool(re.match(r"^[A-Za-z\s]+$", name))

    def update_college_details(event):
        selected_college = college_var.get()
        college_code_var.set(college_data[selected_college]["code"])
        programs = list(college_data[selected_college]["programs"].keys())
        program_ent["values"] = programs
        program_ent.current(0)
        update_program_code(None)

    def update_program_code(event):
        selected_college = college_var.get()
        selected_program = program_var.get()
        if selected_program:
            program_code = college_data[selected_college]["programs"].get(selected_program, "")
            program_code_var.set(program_code)
        else:
            program_code_var.set("")

    def register_student():
        student_id = studentid_var.get()
        last_name = lastname_var.get()
        first_name = firstname_var.get()

        data = [student_id, last_name, first_name, gender_var.get(),
                college_var.get(), college_code_var.get(), program_var.get(), program_code_var.get(), year_var.get()]

        if "" in data:
            messagebox.showerror("Error", "All fields must be filled.")
            return

        if not validate_student_id(student_id):
            messagebox.showerror("Invalid Input", "Student ID must be in the format YYYY-XXXX (e.g., 2024-1234).")
            return
            
        if not validate_name(last_name) or not validate_name(first_name):
            messagebox.showerror("Invalid Input", "First and Last Names should contain only letters.")
            return
        
        if os.path.exists(CSV_STUDENTS):
            with open(CSV_STUDENTS, "r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["Student ID"] == student_id:
                        messagebox.showerror("Duplicate ID", f"A student with ID {student_id} already exists.")
                        return


        save_to_csv(data)
        student_tbl.insert("", "end", values=data)
        clear_fields()
        messagebox.showinfo("Success", "Student registered successfully!")

    def clear_fields():
        studentid_var.set("")
        lastname_var.set("")
        firstname_var.set("")
        gender_var.set("")
        college_var.set(list(college_data.keys())[0])
        update_college_details(None)
        year_var.set("")
    
    college_data = {
        "College of Engineering": {
            "code": "COE",
                "programs": {
                    "Diploma in Chemical Engineering Technology": "DCET",
                    "Bachelor of Science in Ceramic Engineering": "BSCerE",
                    "Bachelor of Science in Civil Engineering": "BSCE",
                    "Bachelor of Science in Electrical Engineering": "BSEE",
                    "Bachelor of Science in Mechanical Engineering": "BSME",
                    "Bachelor of Science in Chemical Engineering": "BSChE",
                    "Bachelor of Science in Metallurgical Engineering": "BSMetE",
                    "Bachelor of Science in Computer Engineering": "BSCpE",
                    "Bachelor of Science in Mining Engineering": "BSMinE",
                    "Bachelor of Science in Electronics & Communications Engineering": "BSECE",
                    "Bachelor of Science in Environmental Engineering": "BSEnET"
                }       
        },
        "College of Science and Mathematics": {
            "code": "CSM",
                "programs": {
                    "Bachelor of Science in Biology(BOTANY)": "BSBio-Bot",
                    "Bachelor of Science in Chemistry": "BSChem",
                    "Bachelor of Science in Mathematics": "BSMath",
                    "Bachelor of Science in Physics": "BSPhys",
                    "Bachelor of Science in Biology(ZOOLOGY)": "BSBio-Zoo",
                    "Bachelor of Science in Biology(Marine)": "BSBio-Mar",
                    "Bachelor of Science in Biology(General)": "BSBio-Gen",
                    "Bachelor of Science in Statistics": "BSStat"
                }
        },
        "College of Computer Studies": {
            "code": "CCS",
                "programs": {
                    "Bachelor of Science in Computer Science": "BSCS",
                    "Bachelor of Science in Information Technology": "BSIT",
                    "Bachelor of Science in Information Systems": "BSIS",
                    "Bachelor of Science in Computer Application" : "BSCA"
                }   
        },
        "College of Education": {
            "code": "CED",
                "programs": {
                "Bachelor of Elementary Education(Science and Mathematics)": "BEEd-SciMath",
                "Bachelor of Elementary Education(Language Education)": "BEEd-Lang",
                "Bachelor of Secondary Education(Biology)": "BSEd-Bio",
                "Bachelor of Secondary Education(Chemistry)": "BSEd-Chem",
                "Bachelor of Secondary Education(Physics)": "BSEd-Phys",
                "Bachelor of Secondary Education(Mathematics)": "BSEd-Math",
                "Bachelor of Physical Education": "BPEd",
                "Bachelor of Technology and Livelihood Education(Home Economics)": "BTLED-HE",
                "Bachelor of Technology and Livelihood Eduction(Industrial Arts)": "BTLed-IA",
                "Bachelor of Technical-Vocational Teacher Education(Drafting Technology)": "BTVTED-DT"
                }
        },
        "College of Arts and Social Sciences": {
            "code": "CAS",
                "programs": {
                    "Bachelor of Arts in English Language Studies": "BA-ELS",
                    "Bachelor of Arts in Literary and Cultural Studies": "BA-LCS",
                    "Bachelor of Arts in Filipino": "BA-FIL",
                    "Bachelor of Arts in Panitikan": "BA-PAN",
                    "Bachelor of Arts in Political Science": "BA-POLSCI",
                    "Bachelor of Arts in Psychology": "BA-PSY",
                    "Bachelor of Arts in Sociology": "BA-SOC",
                    "Bachelor of Arts in History(International History Track)": "BA-HIS-IH",
                    "Bachelor of Science in Philosophy": "BS-PHIL-AE",
                    "Bachelor of Science in Psychology": "BS-PSY"
                }
        },
        "College of Economics, Business & Accountancy": {
            "code": "CEBA",
                "programs": {
                    "Bachelor of Science in Accountancy": "BS-ACC",
                    "Bachelor of Science in Business Administration(Business Economics)": "BSBA-BE",
                    "Bachelor of Science in Business Administration(Marketing Management)": "BSBA-MM",
                    "Bachelor of Science in Entrepreneurship": "BS-ENT",
                    "Bachelor of Science in Hospitality Management" : "BSHM"
                }
        },
        "College of Health Sciences": {
            "code": "CHS",
                "programs": {
                    "Bachelor of Science in Nursing": "BSN"
                }
        }
    }

    
    studentid_var = tk.StringVar()
    lastname_var = tk.StringVar()
    firstname_var = tk.StringVar()
    gender_var = tk.StringVar()
    college_var = tk.StringVar(value=list(college_data.keys())[0])
    college_code_var = tk.StringVar(value=college_data[college_var.get()]["code"])
    program_var = tk.StringVar()
    program_code_var = tk.StringVar()
    year_var = tk.StringVar()

    
    addroot = Toplevel()
    addroot.grab_set()
    addroot.geometry('470x470+220+200')
    addroot.title('Student Management System')
    addroot.config(bg='lightgrey')
    addroot.iconbitmap('mana.ico')
    addroot.resizable(False,False)
    studentId_lbl = tk.Label(addroot, text="Student ID ", font=('times', 17,'bold'),relief=tk.GROOVE,borderwidth=3,width=11, bg="lightgrey")
    studentId_lbl.grid(row=0, column=0, padx=2, pady=2)
    studentID_ent = tk.Entry(addroot, bd=7, font=("times", 17),textvariable=studentid_var)
    studentID_ent.grid(row=0, column=1, padx=2, pady=2)

    lastname_lbl = tk.Label(addroot, text="Last Name ", font=('times', 17,'bold'),relief=tk.GROOVE,borderwidth=3,width=11, bg="lightgrey")
    lastname_lbl.grid(row=1, column=0, padx=2, pady=2)
    lastname_ent = tk.Entry(addroot, bd=7, font=("times", 17),textvariable=lastname_var)
    lastname_ent.grid(row=1, column=1, padx=2, pady=2)

    firstname_lbl = tk.Label(addroot, text="First Name ", font=('times', 17,'bold'),relief=tk.GROOVE,borderwidth=3,width=11, bg="lightgrey")
    firstname_lbl.grid(row=2, column=0, padx=2, pady=2)
    firstname_ent = tk.Entry(addroot, bd=7, font=("times", 17),textvariable=firstname_var)
    firstname_ent.grid(row=2, column=1, padx=2, pady=2)
    gender_lbl = tk.Label(addroot, text="Gender ", font=('times', 17, 'bold'),relief=tk.GROOVE,borderwidth=3,width=11, bg="lightgrey")
    gender_lbl.grid(row=3, column=0, padx=2, pady=2)
    gender_var = tk.StringVar()
    gender_ent = ttk.Combobox(addroot, textvariable=gender_var, font=("times", 17),state="readonly")
    gender_ent['values'] = ("","Male", "Female")
    gender_ent.current(0)  
    gender_ent.grid(row=3, column=1, padx=2, pady=2)
    college_lbl = tk.Label(addroot, text="College", font=('times', 17,'bold'),relief=tk.GROOVE,borderwidth=3,width=11, bg="lightgrey")
    college_lbl.grid(row=4, column=0, padx=2, pady=2)
    college_ent = ttk.Combobox(addroot, textvariable=college_var, font=("times", 17), state="readonly",values=list(college_data.keys()))
    college_ent.grid(row=4, column=1, padx=2, pady=2)
    college_ent.bind("<<ComboboxSelected>>", update_college_details)
    college_code_lbl = tk.Label(addroot, text="College Code ", font=('times', 17,'bold'),relief=tk.GROOVE,borderwidth=3,width=11, bg="lightgrey")
    college_code_lbl.grid(row=5, column=0, padx=2, pady=2)
    college_code_var = tk.StringVar(value=college_data[college_var.get()]["code"])
    college_code_ent = tk.Entry(addroot, textvariable=college_code_var, font=('times', 19), state="readonly")
    college_code_ent.grid(row=5, column=1, padx=2, pady=2)
    program_lbl = tk.Label(addroot, text="Program ", font=('times', 17,'bold'),relief=tk.GROOVE,borderwidth=3,width=11, bg="lightgrey")
    program_lbl.grid(row=6, column=0, padx=2, pady=2)
    program_var = tk.StringVar()
    program_ent = ttk.Combobox(addroot, textvariable=program_var, font=("times", 17), state="readonly")
    program_ent['values'] = list(college_data[college_var.get()]["programs"].keys())
    program_ent.current(0)
    program_ent.grid(row=6, column=1, padx=2, pady=2)
    program_ent.bind("<<ComboboxSelected>>", update_program_code)
    program_code_lbl = tk.Label(addroot, text="Program Code ", font=('times', 19,'bold'),relief=tk.GROOVE,borderwidth=3,width=11, bg="lightgrey")
    program_code_lbl.grid(row=7, column=0, padx=2, pady=2)
    program_code_var = tk.StringVar()
    program_code_ent = tk.Entry(addroot, textvariable=program_code_var, font=('times', 19), state="readonly")
    program_code_ent.grid(row=7, column=1, padx=2, pady=2)
    year_lbl = tk.Label(addroot, text="Year level ", font=('times', 17,'bold'),relief=tk.GROOVE,borderwidth=3,width=11, bg="lightgrey")
    year_lbl.grid(row=8, column=0, padx=2, pady=2)
    year_ent = ttk.Combobox(addroot, font=("times", 17), state="readonly",textvariable=year_var)
    year_ent['values'] = ("1", "2", "3", "4")
    year_ent.grid(row=8, column=1, padx=2, pady=2)
    
    update_program_code(None)

    regs_btn = tk.Button(addroot,bg="lightgrey",text="    Register",command=register_student,bd=7,font=("Arial",13),width=18)
    regs_btn.place(x=50,y=390)
    
    clear_btn = tk.Button(addroot,bg="lightgrey",text="Clear",command=clear_fields,bd=7,font=("Arial",13),width=18)
    clear_btn.place(x=250,y=390)
    addroot.mainloop()
    
def update_student():
    selected_item = student_tbl.focus()  

    if not selected_item:
        messagebox.showerror("Error", "No student selected for update.")
        return
    
    student_data = student_tbl.item(selected_item, "values")

    def update_college_details(event):
        selected_college = college_var.get()
        college_code_var.set(college_data[selected_college]["code"])
        programs = list(college_data[selected_college]["programs"].keys())
        program_ent["values"] = programs

        if program_var.get() in programs:
            program_ent.set(program_var.get())
        else:
            program_ent.current(0)

        update_program_code(None)

    def update_program_code(event):
        selected_college = college_var.get()
        selected_program = program_var.get()
        program_code = college_data[selected_college]["programs"].get(selected_program, "")
        program_code_var.set(program_code)

    def update_student_tbl():
        data = [studentid_var.get(), lastname_var.get(), firstname_var.get(), gender_var.get(),
                college_var.get(), college_code_var.get(), program_var.get(), program_code_var.get(), year_var.get()]
        if "" in data:
            messagebox.showerror("Error", "All fields must be filled.")
            return
        if not re.match(r"^\d{4}-\d{4}$", studentid_var.get()):
            messagebox.showerror("Invalid Input", "Student ID must be in the format YYYY-XXXX.")
            return
        if not re.match(r"^[A-Za-z\s]+$", lastname_var.get()) or not re.match(r"^[A-Za-z\s]+$", firstname_var.get()):
            messagebox.showerror("Invalid Input", "Names must contain only letters.")
            return
        current_student_id = student_data[0]
        new_student_id = studentid_var.get()

        if os.path.exists(CSV_STUDENTS):
            with open(CSV_STUDENTS, "r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["Student ID"] == new_student_id and row["Student ID"] != current_student_id:
                        messagebox.showerror("Duplicate ID", f"A student with ID {new_student_id} already exists.")
                        return


        student_tbl.item(selected_item, values=data)
        update_csv_from_table()
        messagebox.showinfo("Updated", "Student details updated successfully!")
        upgroot.destroy()
        

    college_data = {
        "College of Engineering": {
            "code": "COE",
                "programs": {
                    "Diploma in Chemical Engineering Technology": "DCET",
                    "Bachelor of Science in Ceramic Engineering": "BSCerE",
                    "Bachelor of Science in Civil Engineering": "BSCE",
                    "Bachelor of Science in Electrical Engineering": "BSEE",
                    "Bachelor of Science in Mechanical Engineering": "BSME",
                    "Bachelor of Science in Chemical Engineering": "BSChE",
                    "Bachelor of Science in Metallurgical Engineering": "BSMetE",
                    "Bachelor of Science in Computer Engineering": "BSCpE",
                    "Bachelor of Science in Mining Engineering": "BSMinE",
                    "Bachelor of Science in Electronics & Communications Engineering": "BSECE",
                    "Bachelor of Science in Environmental Engineering": "BSEnET"
                }       
        },
        "College of Science and Mathematics": {
            "code": "CSM",
                "programs": {
                    "Bachelor of Science in Biology(BOTANY)": "BSBio-Bot",
                    "Bachelor of Science in Chemistry": "BSChem",
                    "Bachelor of Science in Mathematics": "BSMath",
                    "Bachelor of Science in Physics": "BSPhys",
                    "Bachelor of Science in Biology(ZOOLOGY)": "BSBio-Zoo",
                    "Bachelor of Science in Biology(Marine)": "BSBio-Mar",
                    "Bachelor of Science in Biology(General)": "BSBio-Gen",
                    "Bachelor of Science in Statistics": "BSStat"
                }
        },
        "College of Computer Studies": {
            "code": "CCS",
                "programs": {
                    "Bachelor of Science in Computer Science": "BSCS",
                    "Bachelor of Science in Information Technology": "BSIT",
                    "Bachelor of Science in Information Systems": "BSIS",
                    "Bachelor of Science in Computer Application" : "BSCA"
                }   
        },
        "College of Education": {
            "code": "CED",
                "programs": {
                "Bachelor of Elementary Education(Science and Mathematics)": "BEEd-SciMath",
                "Bachelor of Elementary Education(Language Education)": "BEEd-Lang",
                "Bachelor of Secondary Education(Biology)": "BSEd-Bio",
                "Bachelor of Secondary Education(Chemistry)": "BSEd-Chem",
                "Bachelor of Secondary Education(Physics)": "BSEd-Phys",
                "Bachelor of Secondary Education(Mathematics)": "BSEd-Math",
                "Bachelor of Physical Education": "BPEd",
                "Bachelor of Technology and Livelihood Education(Home Economics)": "BTLED-HE",
                "Bachelor of Technology and Livelihood Eduction(Industrial Arts)": "BTLed-IA",
                "Bachelor of Technical-Vocational Teacher Education(Drafting Technology)": "BTVTED-DT"
                }
        },
        "College of Arts and Social Sciences": {
            "code": "CAS",
                "programs": {
                    "Bachelor of Arts in English Language Studies": "BA-ELS",
                    "Bachelor of Arts in Literary and Cultural Studies": "BA-LCS",
                    "Bachelor of Arts in Filipino": "BA-FIL",
                    "Bachelor of Arts in Panitikan": "BA-PAN",
                    "Bachelor of Arts in Political Science": "BA-POLSCI",
                    "Bachelor of Arts in Psychology": "BA-PSY",
                    "Bachelor of Arts in Sociology": "BA-SOC",
                    "Bachelor of Arts in History(International History Track)": "BA-HIS-IH",
                    "Bachelor of Science in Philosophy": "BS-PHIL-AE",
                    "Bachelor of Science in Psychology": "BS-PSY"
                }
        },
        "College of Economics, Business & Accountancy": {
            "code": "CEBA",
                "programs": {
                    "Bachelor of Science in Accountancy": "BS-ACC",
                    "Bachelor of Science in Business Administration(Business Economics)": "BSBA-BE",
                    "Bachelor of Science in Business Administration(Marketing Management)": "BSBA-MM",
                    "Bachelor of Science in Entrepreneurship": "BS-ENT",
                    "Bachelor of Science in Hospitality Management" : "BSHM"
                }
        },
        "College of Health Sciences": {
            "code": "CHS",
                "programs": {
                    "Bachelor of Science in Nursing": "BSN"
                }
        }
    }

    studentid_var = tk.StringVar(value=student_data[0])
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
    upgroot.geometry('470x470+220+200')
    upgroot.title('Update Student Data')
    upgroot.config(bg='lightgrey')
    upgroot.resizable(False, False)

    tk.Label(upgroot, text="Student ID ", font=('times', 17, 'bold'), relief=tk.GROOVE,borderwidth=3, width=11, bg="lightgrey").grid(row=0, column=0, padx=2, pady=2)
    tk.Entry(upgroot, bd=7, font=("times", 17), textvariable=studentid_var).grid(row=0, column=1, padx=2, pady=2)
    tk.Label(upgroot, text="Last Name ", font=('times', 17, 'bold'), relief=tk.GROOVE,borderwidth=3, width=11, bg="lightgrey").grid(row=1, column=0, padx=2, pady=2)
    tk.Entry(upgroot, bd=7, font=("times", 17), textvariable=lastname_var).grid(row=1, column=1, padx=2, pady=2)
    tk.Label(upgroot, text="First Name ", font=('times', 17, 'bold'), relief=tk.GROOVE,borderwidth=3, width=11, bg="lightgrey").grid(row=2, column=0, padx=2, pady=2)
    tk.Entry(upgroot, bd=7, font=("times", 17), textvariable=firstname_var).grid(row=2, column=1, padx=2, pady=2)
    tk.Label(upgroot, text="Gender ", font=('times', 17, 'bold'), relief=tk.GROOVE,borderwidth=3, width=11, bg="lightgrey").grid(row=3, column=0, padx=2, pady=2)
    gender_ent = ttk.Combobox(upgroot, textvariable=gender_var, font=("times", 17), state="readonly",values=["Male", "Female"])
    gender_ent.grid(row=3, column=1, padx=2, pady=2)
    tk.Label(upgroot, text="College", font=('times', 17, 'bold'), relief=tk.GROOVE,borderwidth=3, width=11, bg="lightgrey").grid(row=4, column=0, padx=2, pady=2)
    college_ent = ttk.Combobox(upgroot, textvariable=college_var, font=("times", 17), state="readonly",values=list(college_data.keys()))
    college_ent.grid(row=4, column=1, padx=2, pady=2)
    college_ent.bind("<<ComboboxSelected>>", update_college_details)
    tk.Label(upgroot, text="College Code ", font=('times', 17, 'bold'), relief=tk.GROOVE,borderwidth=3, width=11, bg="lightgrey").grid(row=5, column=0, padx=2, pady=2)
    tk.Entry(upgroot, textvariable=college_code_var, font=('times', 19), state="readonly").grid(row=5, column=1, padx=2, pady=2)
    tk.Label(upgroot, text="Program ", font=('times', 17, 'bold'), relief=tk.GROOVE,borderwidth=3, width=11, bg="lightgrey").grid(row=6, column=0, padx=2, pady=2)
    program_ent = ttk.Combobox(upgroot, textvariable=program_var, font=("times", 17), state="readonly",values=list(college_data[college_var.get()]["programs"].keys()))
    program_ent.grid(row=6, column=1, padx=2, pady=2)
    program_ent.bind("<<ComboboxSelected>>", update_program_code)
    tk.Label(upgroot, text="Program Code ", font=('times', 19, 'bold'), relief=tk.GROOVE,borderwidth=3, width=11, bg="lightgrey").grid(row=7, column=0, padx=2, pady=2)
    tk.Entry(upgroot, textvariable=program_code_var, font=('times', 19), state="readonly").grid(row=7, column=1, padx=2, pady=2)
    tk.Label(upgroot, text="Year level ", font=('times', 17, 'bold'), relief=tk.GROOVE,borderwidth=3, width=11, bg="lightgrey").grid(row=8, column=0, padx=2, pady=2)
    year_ent = ttk.Combobox(upgroot, font=("times", 17), state="readonly", textvariable=year_var,values=["1", "2", "3", "4"])
    year_ent.grid(row=8, column=1, padx=2, pady=2)
    tk.Button(upgroot, bg="lightgrey", text="Update", command=update_student_tbl, bd=7,font=("Arial", 13), width=18).place(x=50, y=390)
    tk.Button(upgroot, bg="lightgrey", text="Cancel", command=upgroot.destroy, bd=7,font=("Arial", 13), width=18).place(x=250, y=390)

    update_college_details(None)
    
    program_ent.set(student_data[6])  
    
    update_program_code(None)
    
    upgroot.mainloop()
    
win = tk.Tk()
win.geometry("1350x700+0+0")
win.title("Student Management System")
win.configure(bg="#F3EBDF")

filter_frame = tk.LabelFrame(win, text="", font=("Arial", 18, "bold"), bg="#F3EBDF", bd=0)
filter_frame.place(x=250, y=70)

college_filter_var = tk.StringVar()
program_filter_var = tk.StringVar()
sort_by_var = tk.StringVar()

college_dropdown = ttk.Combobox(filter_frame, textvariable=college_filter_var, font=("Arial", 12), state="readonly", width=30)
college_dropdown['values'] = load_colleges()
college_dropdown.current(0)
college_dropdown.grid(row=0, column=0, padx=5, pady=2)

program_dropdown = ttk.Combobox(filter_frame, textvariable=program_filter_var, font=("Arial", 12), state="readonly", width=30)
program_dropdown['values'] = load_programs("All Colleges")
program_dropdown.current(0)
program_dropdown.grid(row=0, column=1, padx=5, pady=2)

def update_program_dropdown(event):
    selected_college = college_filter_var.get()
    program_dropdown['values'] = load_programs(selected_college)
    program_dropdown.current(0)

college_dropdown.bind("<<ComboboxSelected>>", update_program_dropdown)

sort_dropdown = ttk.Combobox(filter_frame, textvariable=sort_by_var, font=("Arial", 12), state="readonly", width=30)
sort_dropdown['values'] = ["First Name A-Z", "First Name Z-A","Last Name A-Z","Last Name Z-A", "Gender", "Year"]
sort_dropdown.current(0)
sort_dropdown.grid(row=0, column=2, padx=5, pady=2)

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

register_btn = tk.Button(text = "Register Student",width=40,font=('Arial',18,'bold'),fg="#F3EBDF",bg='#6A1314',activebackground='blue',relief=tk.GROOVE,activeforeground='white',command=register_student_btn)
register_btn.place(x=30,y=10,width=250,height=40)

refreshicon=tk.PhotoImage(file="refreshicon.png")
show_btn = tk.Button(win,text = "  Refresh  ",compound=tk.RIGHT,image=refreshicon,width=230,height=40,font=('Arial',18,'bold'),fg="#F3EBDF",bd=3,bg='#6A1314',activebackground='blue',relief=tk.GROOVE,activeforeground='white',command=show_all)
show_btn.place(x=350,y=10,width=250,height=40)


update_btn = tk.Button(win,text = "Update",width=12,font=('Arial',15,'bold'),fg="#F3EBDF",bg='#6A1314',activebackground='blue',relief=tk.GROOVE,activeforeground='white',command=update_student)
update_btn.place(x=175,y=650)

delete_btn = tk.Button(win,text = "Delete",width=12,font=('Arial',15,'bold'),fg="#F3EBDF",bg='#6A1314',activebackground='blue',relief=tk.GROOVE,activeforeground='white',command=delete_student)
delete_btn.place(x=575,y=650)

exit_btn = tk.Button(text = "Exit",width=15,font=('Arial',18,'bold'),fg="#F3EBDF",bg='#6A1314',activebackground='blue',relief=tk.GROOVE,activeforeground='white',command=exit_student)
exit_btn.place(x=1025,y=650,width=150,height=40)

tree_frame = tk.Frame(win, bd=3, relief=tk.GROOVE)
tree_frame.place(x=50, y=150, width=1250, height=470)

columns = ("Student ID", "Last Name", "First Name", "Gender", "College", "College Code", "Program", "Program Code", "Year")
student_tbl = ttk.Treeview(tree_frame, columns=columns, show='headings')

for col in columns:
    student_tbl.heading(col, text=col)
    student_tbl.column(col, width=120)

student_tbl.pack(fill=tk.BOTH, expand=True)

def refresh_students():
    for item in student_tbl.get_children():
        student_tbl.delete(item)

    college = college_filter_var.get()
    program = program_filter_var.get()
    sort_option = sort_by_var.get()

    students = load_filtered_students(college, program, sort_option)
    for student in students:
        student_tbl.insert('', 'end', values=[
            student['Student ID'], student['Last Name'], student['First Name'], student['Gender'],
            student['College'], student['College Code'], student['Program'], student['Program Code'], student['Year']
        ])

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

apply_filter_btn = tk.Button(filter_frame, text="Apply Filters", command=refresh_students, font=("Arial", 11), bg="#6A1314", fg="white")
apply_filter_btn.grid(row=1, column=0, columnspan=3, pady=5)
refresh_students()
win.mainloop()
