import hashlib
import random
import re
import secrets
import smtplib
import ssl
import string
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pyotp
from PIL import Image

from core.auth.crud.configuration import ConfigurationCrud
from core.auth.enum import NotStrongPasswordErrorMessage
from core.exception import (
    InvalidOneTimeTokenError,
    OTPFailedAttemptsError,
    SendMailException,
)
from core.redis import Redis


def generate_one_time_token(user_id: str, key: str | None = None):
    if key is None:
        key = pyotp.random_base32()
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    if Redis.exists(key):
        return generate_one_time_token(user_id, key_hash)
    else:
        Redis.set(key_hash, user_id, exp=timedelta(minutes=10))
        return key_hash


def get_user_id_by_one_time_token(one_time_token: str):
    user_id = Redis.get(one_time_token)
    Redis.delete(one_time_token)
    if user_id is None:
        raise InvalidOneTimeTokenError()
    return user_id


def generate_digit_code():
    secret_key = pyotp.random_base32()
    totp = pyotp.TOTP(secret_key)
    return totp.now()


def check_digit_code_failed_attempts(email):
    failed_attempts = int(Redis.get(f"{email}_failed_attempts"))
    if failed_attempts >= 2:
        Redis.delete(f"{email}_digit_code")
        raise OTPFailedAttemptsError()

    failed_attempts += 1
    Redis.set(
        f"{email}_failed_attempts",
        f"{failed_attempts}",
    )


def send_mail(to_email: str, subject: str, body: str):
    try:
        configuration = ConfigurationCrud.get_partial({}, ["email_configuration"])
        configuration = configuration.email_configuration
        context = ssl.create_default_context()
        smtp_server = smtplib.SMTP_SSL(
            configuration.server, configuration.port, context
        )
        smtp_server.ehlo()
        smtp_server.login(configuration.email_address, configuration.password)

        message = MIMEMultipart()
        message["From"] = configuration.email_address
        message["To"] = to_email
        message["Subject"] = subject

        text = MIMEText(body, "html")
        message.attach(text)

        smtp_server.sendmail(configuration.email_address, to_email, message.as_string())
    except:
        raise SendMailException()
    finally:
        smtp_server.close()


def get_mail_template(firstname, digit_code):
    return f"""
    <div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">
        <div style="margin:50px auto;width:70%;padding:20px 0">
            <div style="border-bottom:1px solid #eee">
            <a href="" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">APP</a>
            </div>
            <p style="font-size:1.1em">Hi {firstname},</p>
            <p>Use the following OTP to complete your Sign Up procedures. OTP is valid for 3 minutes</p>
            <h2 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{digit_code}</h2>
            <hr style="border:none;border-top:1px solid #eee" />
            <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
            <p>App</p>
            </div>
        </div>
        </div>
    """


def get_register_mail_template(invite_links):
    return f"""
    <div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">
        <div style="margin:50px auto;width:70%;padding:20px 0">
            <div style="border-bottom:1px solid #eee">
            <a href="" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">APP</a>
            </div>
            <p style="font-size:1.1em">Hi,</p>
            <p>You have been invited to join our platform</p>
            <p>Click on the link below to register:</p>
            <h2 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;"><a href={invite_links}>{invite_links}</a></h2>
            <hr style="border:none;border-top:1px solid #eee" />
            <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
            <p>Best regards,</p>
            <p>App Team</p>
            </div>
        </div>
        </div>
    """


def generate_invite_token():
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(16)
    )


def generate_password():
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(16))


def is_strong_password(password) -> NotStrongPasswordErrorMessage:
    length_regex = re.compile(r".{8,}")
    uppercase_regex = re.compile(r"[A-Z]")
    lowercase_regex = re.compile(r"[a-z]")
    digit_regex = re.compile(r"\d")
    special_regex = re.compile(r"[!@#$%^&*()]")

    if not length_regex.search(password):
        return NotStrongPasswordErrorMessage.LENGTH

    if not uppercase_regex.search(password):
        return NotStrongPasswordErrorMessage.UPPERCASE

    if not lowercase_regex.search(password):
        return NotStrongPasswordErrorMessage.LOWERCASE

    if not digit_regex.search(password):
        return NotStrongPasswordErrorMessage.DIGIT

    if not special_regex.search(password):
        return NotStrongPasswordErrorMessage.SPECIAL

    return NotStrongPasswordErrorMessage.SUCCESS


def resize_image(
    image_path: str,
    new_size: tuple[float, float],
    thumbnail_size: tuple[int, int],
):
    with open(image_path, "rb") as img:
        image = Image.open(img)
        image.resize(new_size)
        image.thumbnail(thumbnail_size)
        image.save(image_path)
