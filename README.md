# Fake SMTP Email Saver

A simple fake SMTP server for dev/testing purposes.

## Features

1. **Email Saving:**
   - Every email received is saved in the `email/` directory with a timestamp-based folder structure.
   - Saves email metadata, plain text content, HTML content, and attachments.
   - Creates three files for each email:
     - `email.txt`: Human-readable summary of the email.
     - `email.json`: JSON representation of the email details.
     - `email.html`: If the email contains HTML content, it is saved here.
   - Attachments are saved in a subdirectory called `attachments/`.

2. **Web Server:**
   - A lightweight HTTP server serves the `email/` directory for easy browsing of saved emails.
   - Accessible through a configurable port (default: 8080).

3. **Configurable Logging:**
   - Logs can be directed to the terminal, a file, or both.
   - Provides detailed logs of incoming emails and their processing.

4. **Customizable Server:**
   - Hostname and port can be specified via CLI arguments.

## Motivation

Developers often need a way to test email-sending features in applications without risking actual email delivery. This project offers a local solution, simplifying debugging and ensuring no accidental emails are sent during testing. The added web interface provides a convenient way to access saved emails without manually navigating the filesystem.

## How It Works

1. **Start the Server:**
   - Run the script with the desired configuration:
     ```sh
     python fakesmtp.py --host localhost --port 1025 --logging both --web-port 8080
     ```

2. **Send Test Emails:**
   - Configure your application or email client to use the fake SMTP server:
     - SMTP Host: `localhost`
     - SMTP Port: `1025` (or as specified via CLI arguments)

3. **View Saved Emails:**
   - Emails are saved in the `email/` directory, organized by timestamp.
   - Open a browser and navigate to `http://localhost:8080` to browse emails through the web interface.

## CLI Arguments

| Argument       | Description                                      | Default Value |
|----------------|--------------------------------------------------|---------------|
| `--host`       | Hostname the SMTP server listens on              | `localhost`   |
| `--port`       | Port the SMTP server listens on                  | `1025`        |
| `--logging`    | Logging output: `terminal`, `file`, or `both`    | `both`        |
| `--web-port`   | Port the web server listens on                   | `8080`        |

## License

This project is licensed under the **MIT License**, allowing free use, modification, and distribution. It’s an open-source solution meant to simplify email testing and debugging for developers worldwide.
