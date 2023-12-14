import tkinter as tk
from tkinter import filedialog
from email_sender import EmailSender

class EmailSenderUI:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        self.file_path_label = tk.Label(self.root, text="File Path:")
        self.file_path_label.pack()

        self.file_path_entry = tk.Entry(self.root)
        self.file_path_entry.pack()

        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_file)
        self.browse_button.pack()

        self.recipient_label = tk.Label(self.root, text="Recipient Email:")
        self.recipient_label.pack()

        self.recipient_entry = tk.Entry(self.root)
        self.recipient_entry.pack()

        self.subject_label = tk.Label(self.root, text="Subject:")
        self.subject_label.pack()

        self.subject_entry = tk.Entry(self.root)
        self.subject_entry.pack()

        self.body_label = tk.Label(self.root, text="Body:")
        self.body_label.pack()

        self.body_entry = tk.Text(self.root, height=5)
        self.body_entry.pack()

        self.upload_button = tk.Button(self.root, text="Upload File and Send Email", command=self.upload_file_and_send_email)
        self.upload_button.pack()

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()

        self.clear_fields_button = tk.Button(self.root, text="Clear Fields", command=self.clear_fields)
        self.clear_fields_button.pack()

    def browse_file(self):
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(tk.END, filedialog.askopenfilename())

    def upload_file_and_send_email(self):
        email_sender = EmailSender()  # Create a new EmailSender instance for each operation
        file_path = self.file_path_entry.get()
        recipient_email = self.recipient_entry.get()
        subject = self.subject_entry.get()
        body = self.body_entry.get("1.0", tk.END)

        success, file_url = email_sender.upload_file(file_path)
        
        if success:
            email_success = email_sender.send_email(recipient_email, subject, body, file_url)
            if email_success:
                self.status_label.config(text="File uploaded successfully and email sent!")
            else:
                self.status_label.config(text="Email sending failed. Please check recipient email.")
        else:
            self.status_label.config(text="File upload failed. Please check the file path.")


    def clear_fields(self):
        self.file_path_entry.delete(0, tk.END)
        self.recipient_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.body_entry.delete("1.0", tk.END)
        self.status_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("FTP File Upload and Email")

    email_sender_ui = EmailSenderUI(root)
    
    root.mainloop()