import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_email_otp(user_email, otp_code, username="Operator"):
    """
    Sends the 6-digit 2FA verification code directly to the user's Gmail.
    """
    subject = f"Your StockPilot Verification Code: {otp_code}"
    message = (
        f"Hello {username},\n\n"
        f"Your one-time login verification code is: {otp_code}\n\n"
        f"This code will expire in 5 minutes.\n"
        f"If you did not request this login, please change your password immediately.\n\n"
        f"Enterprise Operations Security Team"
    )

    
    print("\n" + "=" * 50)
    print(f"--> [GMAIL DISPATCH] Sending to: {user_email}")
    print(f"--> [StockPilot OTP Code]: {otp_code}")
    print("=" * 50 + "\n")

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email OTP: {e}")
        print("--> [EMAIL ERROR]:", e)
        return False