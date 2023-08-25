import wx
from student_payments import BackEnd
from datetime import datetime

class MyApp(wx.Frame):
    def __init__(self, parent, title):
        super(MyApp, self).__init__(parent, title=title, size=(350, 450))
        self.backend = BackEnd()

        # UI elements
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Combobox for commands
        command_lbl = wx.StaticText(panel, label="Command:")

        self.commands = ["All students", "add student", "show student", "add transaction"]
        self.command_combobox = wx.ComboBox(panel, choices=self.commands, style=wx.CB_READONLY)
        self.command_combobox.SetSelection(0)  # Set "All students" as the default option
        vbox.Add(command_lbl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(self.command_combobox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        self.command_combobox.Bind(wx.EVT_COMBOBOX, self.on_combobox_change)

        # Student name field
        self.student_name_lbl = wx.StaticText(panel, label="Student Name:")
        self.student_name_entry = wx.TextCtrl(panel)
        vbox.Add(self.student_name_lbl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(self.student_name_entry, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        # Initially hide the student name label and entry
        self.student_name_lbl.Hide()
        self.student_name_entry.Hide()

        # Transaction amount field
        self.transaction_amount_lbl = wx.StaticText(panel, label="Transaction Amount:")
        self.transaction_amount_entry = wx.TextCtrl(panel)
        vbox.Add(self.transaction_amount_lbl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(self.transaction_amount_entry, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Transaction date field
        self.transaction_date_lbl = wx.StaticText(panel, label="Transaction Date (mm-dd-yyyy):")
        self.transaction_date_entry = wx.TextCtrl(panel)
        vbox.Add(self.transaction_date_lbl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(self.transaction_date_entry, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Initially hide the transaction amount and date fields
        self.transaction_amount_lbl.Hide()
        self.transaction_amount_entry.Hide()
        self.transaction_date_lbl.Hide()
        self.transaction_date_entry.Hide()

        # Button
        self.button = wx.Button(panel, label="Submit")
        vbox.Add(self.button, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        self.button.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.button.Hide()

        # Create a ScrolledWindow for status message
        self.status_window = wx.ScrolledWindow(panel, style=wx.VSCROLL)
        self.status_window_sizer = wx.BoxSizer(wx.VERTICAL)  # A sizer for the content inside ScrolledWindow

        # Status message below the button
        self.status_msg = wx.StaticText(self.status_window, label="")  # Note that parent is changed to self.status_window
        self.status_window_sizer.Add(self.status_msg, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        # Set the sizer to ScrolledWindow and define the scroll rate
        self.status_window.SetSizer(self.status_window_sizer)
        self.status_window.SetScrollRate(0, 20)  # Only vertical scroll with 20 pixels rate

        vbox.Add(self.status_window, 1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)  # Add ScrolledWindow to the main sizer

        # Setting the layout
        panel.SetSizer(vbox)
        
        # Display all students' names and balances by default
        self.display_all_students()
        
    def display_all_students(self):
        student_data = self.backend.show_all_students_api()
        display_data = []
        for student_name, balance in student_data.items():
            display_data.append(f"{student_name}: ${balance}")
        self.status_msg.SetLabel('\n'.join(display_data))

    def on_button_click(self, event):
        student_name = self.student_name_entry.GetValue().strip()

        if not self.validate_student_name(student_name):
            wx.MessageBox("Invalid student name. Please enter only the first name or first name followed by a last name without any additional whitespace.", "Error", wx.OK | wx.ICON_ERROR)
            return

        selected_command = self.command_combobox.GetValue()

        if selected_command == "add student":
            response = self.backend.add_student_api(student_name)
            self.status_msg.SetLabel(response["message"])
            if response["status"] == "success":
                self.backend.dump_students()

        elif selected_command == "show student":
            response = self.backend.show_transactions_api(student_name)
            if response["status"] == "success":
                balance_info = f"Showing student {student_name} info. Total balance: {response['balance']}\n"
                
                transaction_info = "\n".join([
                    f"Transaction ID: {t['transaction_id']}, Amount: {t['amount']}, Date: {t['date'].strftime('%m-%d-%y')}" 
                    for t in response['transactions']
                ])
                
                complete_info = balance_info + "\n" + transaction_info
                self.status_msg.SetLabel(complete_info)
                
            else:
                self.status_msg.SetLabel(response["message"])

        elif selected_command == "add transaction":
            transaction_amount = self.transaction_amount_entry.GetValue()
            transaction_date = self.transaction_date_entry.GetValue().strip()

            # If no date is provided, use current date by default
            if not transaction_date:
                transaction_date = datetime.now().strftime('%m-%d-%Y')
            else:
                if not self.validate_transaction_date(transaction_date):
                    wx.MessageBox("Invalid transaction date format. Please enter date in mm-dd-yyyy format or leave blank for current date.", "Error", wx.OK | wx.ICON_ERROR)
                    return
            
            if self.validate_transaction_amount(transaction_amount):
                response = self.backend.add_transaction_api(student_name, float(transaction_amount), transaction_date)
                self.status_msg.SetLabel(response["message"])
                if response["status"] == "success":
                    self.backend.dump_transactions()
            else:
                wx.MessageBox("Invalid transaction amount. Please enter a valid float number.", "Error", wx.OK | wx.ICON_ERROR)
                return

        self.Layout()  # Refresh the layout to display the new message properly
        self.Refresh()

    def on_combobox_change(self, event):
        # Clear the status message
        self.status_msg.SetLabel("")

        selected_command = self.command_combobox.GetValue()

        if selected_command == "All students":
            self.student_name_lbl.Hide()
            self.student_name_entry.Hide()
            self.transaction_amount_lbl.Hide()
            self.transaction_amount_entry.Hide()
            self.transaction_date_lbl.Hide()  # Hide transaction date field
            self.transaction_date_entry.Hide()  # Hide transaction date field
            self.button.Hide()

            # Fetch data and update status message
            students_balance = self.backend.show_all_students_api()
            balance_messages = [f"{student_name}: ${balance}" for student_name, balance in students_balance.items()]
            self.status_msg.SetLabel("\n".join(balance_messages))
            
        elif selected_command == "add transaction":
            self.student_name_lbl.Show()
            self.student_name_entry.Show()
            self.transaction_amount_lbl.Show()
            self.transaction_amount_entry.Show()
            self.transaction_date_lbl.Show()  # Show transaction date field
            self.transaction_date_entry.Show()  # Show transaction date field
            self.button.Show()

        elif selected_command == "add student":
            self.student_name_lbl.Show()
            self.student_name_entry.Show()
            self.transaction_amount_lbl.Hide()
            self.transaction_amount_entry.Hide()
            self.transaction_date_lbl.Hide()  # Hide transaction date field
            self.transaction_date_entry.Hide()  # Hide transaction date field
            self.button.Show()

        elif selected_command == "show student":
            self.student_name_lbl.Show()
            self.student_name_entry.Show()
            self.transaction_amount_lbl.Hide()
            self.transaction_amount_entry.Hide()
            self.transaction_date_lbl.Hide()  # Hide transaction date field
            self.transaction_date_entry.Hide()  # Hide transaction date field
            self.button.Show()

        self.Layout()
        self.Refresh()

    def validate_student_name(self, name):
        if not name.strip():
            return False
        parts = name.split()
        if 1 <= len(parts) <= 2:
            return True
        return False

    def validate_transaction_amount(self, amount):
        try:
            float(amount)
            return True
        except ValueError:
            return False
        
    def validate_transaction_date(self, date):
        try:
            datetime.strptime(date, '%m-%d-%Y')
            return True
        except ValueError:
            return False

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyApp(None, "Student management")
    frame.SetSize((300, 400))
    frame.Show()
    app.MainLoop()
