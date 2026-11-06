import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# ---------------- STUDENT CLASS ----------------

class Student:
    def __init__(self, roll, name, course, marks):
        self.roll = roll
        self.name = name
        self.course = course
        self.marks = marks

    def calculate_grade(self):
        if self.marks >= 90:
            return "A+"
        elif self.marks >= 80:
            return "A"
        elif self.marks >= 70:
            return "B"
        elif self.marks >= 60:
            return "C"
        elif self.marks >= 40:
            return "D"
        else:
            return "F"

    def to_dict(self):
        return {
            "roll": self.roll,
            "name": self.name,
            "course": self.course,
            "marks": self.marks
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["roll"],
            data["name"],
            data["course"],
            data["marks"]
        )


# ---------------- DATA MANAGEMENT ----------------

class StudentManager:

    FILE_NAME = "students.json"

    def __init__(self):
        self.students = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.FILE_NAME):
            try:
                with open(self.FILE_NAME, "r") as file:
                    data = json.load(file)

                self.students = [
                    Student.from_dict(item) for item in data
                ]

            except (json.JSONDecodeError, KeyError, TypeError):
                self.students = []
        else:
            self.students = []

    def save_data(self):
        with open(self.FILE_NAME, "w") as file:
            json.dump(
                [student.to_dict() for student in self.students],
                file,
                indent=4
            )

    def add_student(self, student):
        for s in self.students:
            if s.roll == student.roll:
                return False

        self.students.append(student)
        self.save_data()
        return True

    def update_student(self, roll, name, course, marks):
        for student in self.students:
            if student.roll == roll:
                student.name = name
                student.course = course
                student.marks = marks
                self.save_data()
                return True

        return False

    def delete_student(self, roll):
        for student in self.students:
            if student.roll == roll:
                self.students.remove(student)
                self.save_data()
                return True

        return False

    def search_student(self, keyword):
        result = []

        for student in self.students:
            if (keyword.lower() in student.name.lower()
                    or keyword.lower() in student.roll.lower()):
                result.append(student)

        return result

    def get_statistics(self):
        total = len(self.students)

        if total == 0:
            return 0, 0, 0

        average = sum(s.marks for s in self.students) / total
        highest = max(s.marks for s in self.students)
        passed = sum(1 for s in self.students if s.marks >= 40)

        return total, average, highest, passed


# ---------------- MAIN APPLICATION ----------------

class StudentApp:

    def __init__(self, root):
        self.root = root
        self.manager = StudentManager()

        self.root.title("Student Management System")
        self.root.geometry("1050x680")
        self.root.minsize(850, 550)
        self.root.configure(bg="#F3F4F6")

        self.setup_style()
        self.create_header()
        self.create_dashboard()
        self.create_table()
        self.refresh_table()

    # ---------------- STYLING ----------------

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="white",
            foreground="#1F2937",
            rowheight=35,
            fieldbackground="white",
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#1E293B",
            foreground="white",
            font=("Arial", 10, "bold"),
            padding=10
        )

        style.map(
            "Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", "#1E3A8A")]
        )

    # ---------------- HEADER ----------------

    def create_header(self):
        header = tk.Frame(self.root, bg="#111827", height=85)
        header.pack(fill="x")

        tk.Label(
            header,
            text="STUDENT MANAGEMENT SYSTEM",
            font=("Arial", 19, "bold"),
            fg="white",
            bg="#111827"
        ).pack(side="left", padx=25, pady=25)

        tk.Label(
            header,
            text="PYTHON PROJECT",
            font=("Arial", 10, "bold"),
            fg="#93C5FD",
            bg="#111827"
        ).pack(side="right", padx=25)

    # ---------------- DASHBOARD ----------------

    def create_dashboard(self):
        self.stats_frame = tk.Frame(
            self.root, bg="#F3F4F6"
        )
        self.stats_frame.pack(fill="x", padx=20, pady=20)

        self.total_label = self.create_card(
            "TOTAL STUDENTS", "0", "#2563EB"
        )

        self.average_label = self.create_card(
            "AVERAGE MARKS", "0", "#7C3AED"
        )

        self.highest_label = self.create_card(
            "HIGHEST MARKS", "0", "#059669"
        )

        self.passed_label = self.create_card(
            "PASSED STUDENTS", "0", "#D97706"
        )

    def create_card(self, title, value, color):
        card = tk.Frame(
            self.stats_frame,
            bg="white",
            highlightbackground="#E5E7EB",
            highlightthickness=1
        )
        card.pack(side="left", expand=True, fill="x", padx=6)

        tk.Label(
            card,
            text=title,
            bg="white",
            fg="#6B7280",
            font=("Arial", 9, "bold")
        ).pack(pady=(15, 5))

        label = tk.Label(
            card,
            text=value,
            bg="white",
            fg=color,
            font=("Arial", 23, "bold")
        )
        label.pack(pady=(0, 15))

        return label

    # ---------------- STUDENT TABLE ----------------

    def create_table(self):
        toolbar = tk.Frame(self.root, bg="#F3F4F6")
        toolbar.pack(fill="x", padx=25, pady=5)

        tk.Label(
            toolbar,
            text="Student Records",
            font=("Arial", 15, "bold"),
            bg="#F3F4F6",
            fg="#111827"
        ).pack(side="left")

        self.search_entry = tk.Entry(
            toolbar,
            font=("Arial", 11),
            width=23,
            relief="solid",
            bd=1
        )
        self.search_entry.pack(side="right", padx=5, ipady=6)
        self.search_entry.bind(
            "<KeyRelease>", self.search_records
        )

        tk.Label(
            toolbar,
            text="Search:",
            bg="#F3F4F6",
            font=("Arial", 10)
        ).pack(side="right")

        table_frame = tk.Frame(self.root, bg="white")
        table_frame.pack(
            fill="both", expand=True, padx=25, pady=12
        )

        columns = (
            "roll", "name", "course", "marks", "grade"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "roll": "Roll Number",
            "name": "Student Name",
            "course": "Course",
            "marks": "Marks",
            "grade": "Grade"
        }

        widths = {
            "roll": 120,
            "name": 220,
            "course": 200,
            "marks": 100,
            "grade": 100
        }

        for col in columns:
            self.table.heading(col, text=headings[col])
            self.table.column(
                col, width=widths[col], anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.pack(
            side="left", fill="both", expand=True
        )
        scrollbar.pack(side="right", fill="y")

        # Action buttons
        buttons = tk.Frame(self.root, bg="#F3F4F6")
        buttons.pack(fill="x", padx=25, pady=(0, 20))

        self.create_button(
            buttons, " + Add Student", "#2563EB",
            self.add_student
        )

        self.create_button(
            buttons, " Edit Student", "#7C3AED",
            self.edit_student
        )

        self.create_button(
            buttons, " Delete Student", "#DC2626",
            self.delete_student
        )

        self.create_button(
            buttons, " Refresh", "#059669",
            self.refresh_table
        )

    def create_button(self, parent, text, color, command):
        tk.Button(
            parent,
            text=text,
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=10,
            command=command
        ).pack(side="left", padx=5)

    # ---------------- REFRESH RECORDS ----------------

    def refresh_table(self, records=None):
        for item in self.table.get_children():
            self.table.delete(item)

        if records is None:
            records = self.manager.students

        for student in records:
            self.table.insert(
                "",
                "end",
                values=(
                    student.roll,
                    student.name,
                    student.course,
                    student.marks,
                    student.calculate_grade()
                )
            )

        self.update_dashboard()

    # ---------------- DASHBOARD UPDATES ----------------

    def update_dashboard(self):
        stats = self.manager.get_statistics()

        if stats == (0, 0, 0):
            total, average, highest, passed = 0, 0, 0, 0
        else:
            total, average, highest, passed = stats

        self.total_label.config(text=str(total))
        self.average_label.config(text=f"{average:.1f}")
        self.highest_label.config(text=str(highest))
        self.passed_label.config(text=str(passed))

    # ---------------- SEARCH ----------------

    def search_records(self, event=None):
        keyword = self.search_entry.get().strip()

        if keyword:
            records = self.manager.search_student(keyword)
        else:
            records = self.manager.students

        self.refresh_table(records)

    # ---------------- STUDENT FORM ----------------

    def student_form(self, title, student=None):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("380x400")
        window.configure(bg="white")
        window.resizable(False, False)
        window.transient(self.root)
        window.grab_set()

        tk.Label(
            window,
            text=title,
            font=("Arial", 17, "bold"),
            bg="white",
            fg="#111827"
        ).pack(pady=20)

        fields = {}

        field_names = [
            "Roll Number",
            "Student Name",
            "Course",
            "Marks"
        ]

        old_values = ["", "", "", ""]

        if student:
            old_values = [
                student.roll,
                student.name,
                student.course,
                str(student.marks)
            ]

        for i, field in enumerate(field_names):
            tk.Label(
                window,
                text=field,
                bg="white",
                font=("Arial", 10, "bold")
            ).pack(anchor="w", padx=35)

            entry = tk.Entry(
                window,
                font=("Arial", 11),
                width=32,
                relief="solid",
                bd=1
            )
            entry.pack(padx=35, pady=(4, 12), ipady=5)

            entry.insert(0, old_values[i])

            if student and i == 0:
                entry.config(state="readonly")

            fields[field] = entry

        def save():
            roll = fields["Roll Number"].get().strip()
            name = fields["Student Name"].get().strip()
            course = fields["Course"].get().strip()
            marks_text = fields["Marks"].get().strip()

            if not all([roll, name, course, marks_text]):
                messagebox.showwarning(
                    "Missing Information",
                    "Please fill in all fields.",
                    parent=window
                )
                return

            try:
                marks = float(marks_text)

                if not 0 <= marks <= 100:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Invalid Marks",
                    "Marks must be a number between 0 and 100.",
                    parent=window
                )
                return

            new_student = Student(
                roll, name, course, marks
            )

            if student:
                success = self.manager.update_student(
                    roll, name, course, marks
                )
                message = "Student updated successfully!"
            else:
                success = self.manager.add_student(new_student)
                message = "Student added successfully!"

            if not success:
                messagebox.showerror(
                    "Duplicate Roll Number",
                    "A student with this roll number already exists.",
                    parent=window
                )
                return

            messagebox.showinfo(
                "Success", message, parent=window
            )

            window.destroy()
            self.refresh_table()

        tk.Button(
            window,
            text="Save Student",
            bg="#2563EB",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            command=save,
            padx=20,
            pady=10
        ).pack(pady=12)

    # ---------------- ADD STUDENT ----------------

    def add_student(self):
        self.student_form("Add New Student")

    # ---------------- EDIT STUDENT ----------------

    def edit_student(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Please select a student first."
            )
            return

        values = self.table.item(selected[0], "values")
        roll = values[0]

        for student in self.manager.students:
            if student.roll == roll:
                self.student_form("Edit Student", student)
                return

    # ---------------- DELETE STUDENT ----------------

    def delete_student(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Please select a student first."
            )
            return

        values = self.table.item(selected[0], "values")
        roll = values[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete {values[1]}?"
        )

        if confirm:
            self.manager.delete_student(roll)
            self.refresh_table()

            messagebox.showinfo(
                "Deleted",
                "Student record deleted successfully."
            )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()