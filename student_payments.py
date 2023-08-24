import csv
from datetime import datetime

class Transaction:
    def __init__(self, transaction_id, student_id, student_name, amount, date=None):
        self.transaction_id = transaction_id
        self.student_id = student_id
        self.student_name = student_name
        self.amount = amount
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        
class Student:
    # A class to represent students
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name

class BackEnd:
    # Main backend class handling the operations
    def __init__(self):
        # Initialize attributes
        self.students = {}
        self.transactions = []
        self.name_to_id = {}
        # Load existing data
        self.initialize_students()
        self.initialize_transactions()

    def initialize_students(self):
        # Load students from CSV file
        try:
            with open('students.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    student_id = int(row['student_id'])
                    self.students[student_id] = row
                    self.name_to_id[row['name']] = student_id
        except FileNotFoundError:
            pass

    def initialize_transactions(self):
        # Load transactions from CSV file
        try:
            with open('transactions.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.transactions.append(row)
                    self.transactions[-1]['transaction_id'] = int(row['transaction_id'])
                    self.transactions[-1]['student_id'] = int(row['student_id'])
                    self.transactions[-1]['amount'] = float(row['amount'])
        except FileNotFoundError:
            pass
    
    # More methods for handling students, transactions, and related operations
    def add_transaction(self, transaction):
        self.transactions.append(vars(transaction))
        print(f"Transaction added for student {transaction.student_name} (ID {transaction.student_id}): {transaction.amount} on {transaction.date}")

    def add_or_update_student(self, student):        
        self.students[student.student_id] = vars(student)
        self.name_to_id[student.name] = student.student_id
        print(f"Student added/updated: ID {student.student_id}, Name {student.name}")

    def dump_students(self):
        with open('students.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['student_id', 'name'])
            writer.writeheader()
            for student in self.students.values():
                writer.writerow(student)

    def dump_transactions(self):
        with open('transactions.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['transaction_id', 'student_id', 'student_name', 'amount', 'date'])
            writer.writeheader()
            writer.writerows(self.transactions)

    def add_student_api(self, name):
        # Check if the student name already exists
        if name in self.name_to_id:
            return {"status": "error", "message": "Student name already exists."}
            
        student_id = self.get_next_student_id()
        student = Student(student_id, name)
        self.add_or_update_student(student)
        return {"status": "success", "message": f"Student {student.name} is added successfully.", "student_id": student_id}

    def add_transaction_api(self, student_name, amount, date=None):
        if student_name not in self.name_to_id:
            return {"status": "error", "message": "Student name not found."}

        transaction_id = self.get_next_transaction_id()
        student_id = self.name_to_id[student_name]
        
        # If date is not provided, use the current date
        if not date:
            date = datetime.now().strftime('%m-%d-%Y')

        transaction = Transaction(transaction_id, student_id, student_name, amount, date)
        self.add_transaction(transaction)
        
        # Formulate the message as specified
        message = f"Transaction for {student_name} of ${amount} for {date} is added successfully"

        return {"status": "success", "message": message}


    def show_transactions_api(self, student_name):
        if student_name not in self.name_to_id:
            return {"status": "error", "message": "Student name not found."}

        student_id = self.name_to_id[student_name]
        student_transactions = [t for t in self.transactions if int(t['student_id']) == student_id]
        balance = sum(float(t['amount']) for t in student_transactions)

        result = {
            "status": "success",
            "student_name": student_name,
            "student_id": student_id,
            "transactions": student_transactions,
            "balance": balance
        }
        return result
    
    def show_all_students_api(self):
        students_balance = {}

        for student_name, student_id in self.name_to_id.items():
            student_transactions = [t for t in self.transactions if int(t['student_id']) == student_id]
            balance = sum(float(t['amount']) for t in student_transactions)
            students_balance[student_name] = balance

        return students_balance
    
    def get_next_student_id(self):
        return max(map(int, self.students.keys()), default=0) + 1

    def get_next_transaction_id(self):
        return max((int(transaction['transaction_id']) for transaction in self.transactions), default=0) + 1
    