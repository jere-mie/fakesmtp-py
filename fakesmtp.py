# *** Fake SMTP Email Saver ***
# Author: Jeremie Bornais
# License: MIT
# Version: 1.0.0
# Feel free to copy, modify, include in your own projects,
# or do pretty much whatever you want with this as you see fit :)

import asyncio
from aiosmtpd.controller import Controller
from email import message_from_bytes
from email.policy import default
import os
import json
from datetime import datetime
import logging
import argparse
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Argument parsing
parser = argparse.ArgumentParser(description="Fake SMTP server with email saving capabilities.")
parser.add_argument("--host", type=str, default="localhost", help="Hostname the server should listen on (default: localhost)")
parser.add_argument("--port", type=int, default=1025, help="Port the server should listen on (default: 1025)")
parser.add_argument("--logging", type=str, choices=["terminal", "file", "both"], default="both", help="Logging output: terminal, file, or both (default: both)")
parser.add_argument("--web-port", type=int, default=8080, help="Port for the web server to serve email directory (default: 8080)")
args = parser.parse_args()

# Configure logging handlers
handlers = []
if args.logging in ["terminal", "both"]:
    handlers.append(logging.StreamHandler())
if args.logging in ["file", "both"]:
    handlers.append(logging.FileHandler("email_server.log"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger(__name__)

class EmailObject:
    def __init__(self, mail_from, rcpt_tos, subject, plain_text, html_content, attachments):
        self.mail_from = mail_from
        self.rcpt_tos = rcpt_tos
        self.subject = subject
        self.plain_text = plain_text
        self.html_content = html_content
        self.attachments = attachments  # List of (filename, content)

    def __repr__(self):
        return (f"EmailObject(\n"
                f"  From: {self.mail_from}\n"
                f"  To: {', '.join(self.rcpt_tos)}\n"
                f"  Subject: {self.subject}\n"
                f"  Plain Text: {self.plain_text}\n"
                f"  HTML Content: {self.html_content}\n"
                f"  Attachments: {[(name, len(content)) for name, content in self.attachments]}\n)")

class SaveEmailHandler:
    async def handle_DATA(self, server, session, envelope):
        logger.info("Received new email")

        # Parse the email message
        msg = message_from_bytes(envelope.content, policy=default)

        # Extract headers
        subject = msg["subject"]
        plain_text = None
        html_content = None
        attachments = []

        # Extract payloads
        if msg.is_multipart():
            for part in msg.iter_parts():
                content_type = part.get_content_type()
                disposition = part.get_content_disposition()

                if content_type == "text/plain" and disposition is None:
                    plain_text = part.get_content()
                elif content_type == "text/html" and disposition is None:
                    html_content = part.get_content()
                elif disposition == "attachment":
                    filename = part.get_filename()  # Get the filename
                    file_content = part.get_content()  # Get the file content
                    attachments.append((filename, file_content))
        else:
            # Non-multipart email
            if msg.get_content_type() == "text/plain":
                plain_text = msg.get_content()
            elif msg.get_content_type() == "text/html":
                html_content = msg.get_content()

        # Create an EmailObject
        email_obj = EmailObject(
            mail_from=envelope.mail_from,
            rcpt_tos=envelope.rcpt_tos,
            subject=subject,
            plain_text=plain_text,
            html_content=html_content,
            attachments=attachments
        )

        # Log email content
        logger.info(f"Email content:\n{email_obj}")

        # Create a directory for this email using current datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        email_dir = os.path.join("email", timestamp)
        attachments_dir = os.path.join(email_dir, "attachments")
        os.makedirs(attachments_dir, exist_ok=True)

        logger.info(f"Saving email to directory: {email_dir}")

        # Save email details to a text file
        email_txt_path = os.path.join(email_dir, "email.txt")
        with open(email_txt_path, "w") as f:
            f.write(f"From: {email_obj.mail_from}\n")
            f.write(f"To: {', '.join(email_obj.rcpt_tos)}\n")
            f.write(f"Subject: {email_obj.subject}\n\n")
            f.write(f"Plain Text Content:\n{email_obj.plain_text}\n\n")
            f.write(f"HTML Content:\n{email_obj.html_content}\n\n")
            f.write(f"Attachments: {', '.join([name for name, _ in email_obj.attachments])}\n")
        logger.info(f"Email details saved to {email_txt_path}")

        # Save email details to a JSON file
        email_json_path = os.path.join(email_dir, "email.json")
        with open(email_json_path, "w") as f:
            json.dump({
                "from": email_obj.mail_from,
                "to": email_obj.rcpt_tos,
                "subject": email_obj.subject,
                "plain_text": email_obj.plain_text,
                "html_content": email_obj.html_content,
                "attachments": [name for name, _ in email_obj.attachments]
            }, f, indent=4)
        logger.info(f"Email details saved to {email_json_path}")

        # Save HTML content to an HTML file
        if email_obj.html_content:
            email_html_path = os.path.join(email_dir, "email.html")
            with open(email_html_path, "w") as f:
                f.write(email_obj.html_content)
            logger.info(f"HTML content saved to {email_html_path}")

        # Save attachments to the attachments directory
        for filename, content in attachments:
            if filename:
                filepath = os.path.join(attachments_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(content)
                logger.info(f"Attachment saved to {filepath}")

        logger.info(f"Email processing complete for {timestamp}")

        return '250 Message accepted for delivery'

def start_web_server():
    web_dir = os.path.join(os.getcwd(), "email")
    os.makedirs(web_dir, exist_ok=True)
    os.chdir(web_dir)

    class CustomHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            logger.info("[HTTP] " + format % args)

    server = HTTPServer((args.host, args.web_port), CustomHandler)
    logger.info(f"Starting web server at http://{args.host}:{args.web_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping web server...")
        server.server_close()

if __name__ == "__main__":
    handler = SaveEmailHandler()
    controller = Controller(handler, hostname=args.host, port=args.port)

    logger.info(f"Starting fake SMTP server on {args.host}:{args.port}")
    controller.start()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Start the web server in a separate thread
        import threading
        web_server_thread = threading.Thread(target=start_web_server, daemon=True)
        web_server_thread.start()

        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Stopping server...")
        controller.stop()
    finally:
        loop.close()
