import smtplib
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, message: str):
    # Configuración básica (ejemplo con Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    from_email = "cristianr.gonzalezi@uqvirtual.edu.co"
    password = "Crisgonza_20"
    
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
