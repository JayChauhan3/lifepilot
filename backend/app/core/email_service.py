import os
import structlog
from typing import Optional
import resend

logger = structlog.get_logger()

class EmailService:
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
        
        if self.api_key:
            resend.api_key = self.api_key
            logger.info("Email service initialized with Resend")
        else:
            logger.warning("RESEND_API_KEY not found - emails will only be logged to console")
    
    def send_verification_email(self, to_email: str, verification_link: str) -> bool:
        """
        Send verification email to user
        
        Args:
            to_email: Recipient email address
            verification_link: Full verification URL
            
        Returns:
            True if email sent successfully, False otherwise
        """
        # If no API key, just log to console (development mode)
        if not self.api_key:
            logger.info("📧 MOCK EMAIL (No Resend API key)", to=to_email, link=verification_link)
            return False
        
        try:
            # Send email using Resend
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": "Verify your LifePilot account",
                "html": self._get_verification_email_html(verification_link)
            }
            
            email = resend.Emails.send(params)
            logger.info("✅ Verification email sent", to=to_email, email_id=email.get("id"))
            return True
            
        except Exception as e:
            logger.error("Failed to send verification email", error=str(e), to=to_email)
            # Fallback to console logging
            logger.info("📧 MOCK EMAIL (Resend failed)", to=to_email, link=verification_link)
            return False
    
    def _get_verification_email_html(self, verification_link: str) -> str:
        """Generate HTML email template for verification"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify your email</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 40px 0;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #1a1a1a; font-size: 28px; font-weight: 600;">
                                LifePilot
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 20px 40px 40px 40px;">
                            <h2 style="margin: 0 0 20px 0; color: #1a1a1a; font-size: 24px; font-weight: 600;">
                                Verify your email address
                            </h2>
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Thanks for signing up! Please verify your email address to complete your registration and start using LifePilot.
                            </p>
                            <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Click the button below to verify your account:
                            </p>
                            
                            <!-- Button -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding: 0 0 30px 0;">
                                        <a href="{verification_link}" 
                                           style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600;">
                                            Verify Email Address
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0 0 10px 0; color: #999999; font-size: 14px; line-height: 1.5;">
                                Or copy and paste this link into your browser:
                            </p>
                            <p style="margin: 0; color: #667eea; font-size: 14px; word-break: break-all;">
                                {verification_link}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 40px; background-color: #f9f9f9; border-top: 1px solid #eeeeee; border-radius: 0 0 8px 8px;">
                            <p style="margin: 0; color: #999999; font-size: 12px; line-height: 1.5; text-align: center;">
                                This verification link will expire in 15 minutes.
                            </p>
                            <p style="margin: 10px 0 0 0; color: #999999; font-size: 12px; line-height: 1.5; text-align: center;">
                                If you didn't create a LifePilot account, you can safely ignore this email.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

# Singleton instance
email_service = EmailService()
