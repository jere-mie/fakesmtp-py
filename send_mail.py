import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

sender_email = "sender@example.com"
recipients = ["recipient1@example.com"]
subject = "Test Email with Attachments"

message = MIMEMultipart()
message["From"] = sender_email
message["To"] = ", ".join(recipients)
message["Subject"] = subject

# content
message.attach(MIMEText("This is the plain text version.", "plain"))
message.attach(MIMEText("<h1>This is the HTML version.</h1>", "html"))

# attachments
files_to_attach = ["README.md", 'requirements.txt']
for file_path in files_to_attach:
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={file_path}",
        )
        message.attach(part)

# send
try:
    with smtplib.SMTP('localhost', 1025) as client:
        client.sendmail(sender_email, recipients, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
