import base64
import binascii
import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

OBFUSCATION_PREFIX = "obf:"


def obfuscate_string(s: str) -> str:
    """
    Reverses a string, encodes it in Base64, and adds a prefix.
    Returns an empty string if the input is empty.
    """
    if not s:
        return ""
    reversed_string = s[::-1]
    encoded_bytes = base64.b64encode(reversed_string.encode("utf-8"))
    return f"{OBFUSCATION_PREFIX}{encoded_bytes.decode('utf-8')}"


def reveal_string(obfuscated_s: str) -> str:
    """
    Decodes a prefixed Base64 string and reverses it to restore the original.
    Returns the input string directly if it's not prefixed, empty, or invalid.
    """
    if not obfuscated_s or not obfuscated_s.startswith(OBFUSCATION_PREFIX):
        return obfuscated_s

    try:
        to_decode = obfuscated_s[len(OBFUSCATION_PREFIX) :]
        # Pad the string with '=' if its length is not a multiple of 4
        padded_to_decode = to_decode + "=" * (-len(to_decode) % 4)
        decoded_bytes = base64.b64decode(padded_to_decode.encode("utf-8"))
        reversed_string = decoded_bytes.decode("utf-8")
        return reversed_string[::-1]
    except (binascii.Error, UnicodeDecodeError):
        # If decoding fails, it might be a normal string that coincidentally
        # started with the prefix. Return it as is.
        return obfuscated_s


def send_email_with_attachment(
    subject: str,
    body: str,
    to_emails: list[str],
    cc_emails: list[str] | None = None,
    attachment_data: bytes | None = None,
    attachment_filename: str = "document.pdf",
) -> bool:
    """
    Sends an email with an optional attachment using SMTP.
    Supports SSL (465) or STARTTLS (587).
    """
    from app.core.config import settings

    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning("SMTP not configured. Email not sent.")
        return False

    try:
        # 1. Create message
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_USER
        msg["To"] = ", ".join(to_emails)
        if cc_emails:
            msg["Cc"] = ", ".join(cc_emails)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # 2. Add attachment
        if attachment_data:
            part = MIMEApplication(attachment_data, Name=attachment_filename)
            part["Content-Disposition"] = f'attachment; filename="{attachment_filename}"'
            msg.attach(part)

        # 3. Connect and send
        recipients = to_emails + (cc_emails or [])

        # Determine connection type
        is_ssl = int(settings.SMTP_PORT) == 465

        if is_ssl:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, int(settings.SMTP_PORT)) as server:
                server.login(settings.SMTP_USER, reveal_string(settings.SMTP_PASSWORD))
                server.sendmail(settings.SMTP_USER, recipients, msg.as_string())
        else:
            with smtplib.SMTP(settings.SMTP_HOST, int(settings.SMTP_PORT)) as server:
                if int(settings.SMTP_PORT) == 587:
                    server.starttls()
                server.login(settings.SMTP_USER, reveal_string(settings.SMTP_PASSWORD))
                server.sendmail(settings.SMTP_USER, recipients, msg.as_string())

        logger.info(f"Email sent to {to_emails}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        return False
