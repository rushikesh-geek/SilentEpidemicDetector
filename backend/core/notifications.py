import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import httpx
from core.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Multi-channel notification service for alerts"""
    
    def __init__(self):
        self.smtp_configured = bool(settings.SMTP_USER and settings.SMTP_PASSWORD)
        self.twilio_configured = bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN)
        
        if self.twilio_configured:
            self.twilio_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
    
    async def send_alert_notifications(self, alert: dict):
        """
        Send notifications for an alert through all configured channels
        
        Args:
            alert: Alert dictionary with all details
        """
        try:
            # Prepare notification content
            subject, message = self._prepare_notification_content(alert)
            
            # Send emails
            if self.smtp_configured:
                emails = settings.get_alert_emails()
                if emails:
                    await self._send_emails(emails, subject, message, alert)
            
            # Send SMS
            if self.twilio_configured:
                phones = settings.get_alert_phones()
                if phones:
                    await self._send_sms(phones, message, alert)
                
                # Send WhatsApp
                if phones:
                    await self._send_whatsapp(phones, message, alert)
            
            # Send to webhooks
            webhooks = settings.get_alert_webhooks()
            if webhooks:
                await self._send_webhooks(webhooks, alert)
            
            logger.info(f"Notifications sent for alert {alert['alert_id']}")
            
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    def _prepare_notification_content(self, alert: dict) -> tuple[str, str]:
        """
        Prepare notification subject and message
        
        Returns:
            Tuple of (subject, message)
        """
        severity = alert["severity"].upper()
        ward = alert["location"]["ward"]
        confidence = alert["confidence"] * 100
        
        subject = f"[{severity}] Disease Outbreak Alert - {ward}"
        
        # Build message
        message = f"""
DISEASE OUTBREAK ALERT

Severity: {severity}
Location: {ward}
Confidence: {confidence:.1f}%
Anomaly Score: {alert['anomaly_score']:.3f}

EVIDENCE:
- Hospital Events: {alert['evidence']['hospital'].get('total_events', 'N/A')}
- Social Mentions: {alert['evidence']['social'].get('total_mentions', 'N/A')}
- Environmental Risk: {alert['evidence']['environment'].get('risk_score', 'N/A')}

RECOMMENDED ACTIONS:
"""
        
        for action in alert['recommended_actions'][:5]:  # Top 5 actions
            message += f"\n[{action['priority'].upper()}] {action['category']}: {action['action']}"
        
        message += f"\n\nAlert ID: {alert['alert_id']}"
        message += f"\nTimestamp: {alert['timestamp']}"
        
        return subject, message
    
    async def _send_emails(self, recipients: List[str], subject: str, message: str, alert: dict):
        """Send email notifications"""
        try:
            # Create HTML version
            html_message = self._create_html_email(alert)
            
            for recipient in recipients:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = settings.SMTP_FROM
                msg["To"] = recipient
                
                # Add plain text and HTML parts
                msg.attach(MIMEText(message, "plain"))
                msg.attach(MIMEText(html_message, "html"))
                
                # Send email
                await aiosmtplib.send(
                    msg,
                    hostname=settings.SMTP_HOST,
                    port=settings.SMTP_PORT,
                    username=settings.SMTP_USER,
                    password=settings.SMTP_PASSWORD,
                    start_tls=True
                )
                
                logger.info(f"Email sent to {recipient}")
                
        except Exception as e:
            logger.error(f"Error sending emails: {e}")
    
    async def _send_sms(self, recipients: List[str], message: str, alert: dict):
        """Send SMS notifications"""
        try:
            # Truncate message for SMS (160 char limit)
            sms_message = f"[{alert['severity'].upper()}] Outbreak Alert - {alert['location']['ward']}\n"
            sms_message += f"Confidence: {alert['confidence']*100:.0f}%\n"
            sms_message += f"Alert ID: {alert['alert_id']}"
            
            for phone in recipients:
                self.twilio_client.messages.create(
                    body=sms_message,
                    from_=settings.TWILIO_FROM_NUMBER,
                    to=phone
                )
                logger.info(f"SMS sent to {phone}")
                
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
    
    async def _send_whatsapp(self, recipients: List[str], message: str, alert: dict):
        """Send WhatsApp notifications"""
        try:
            # Prepare WhatsApp message
            wa_message = f"*[{alert['severity'].upper()}] DISEASE OUTBREAK ALERT*\n\n"
            wa_message += f"📍 Location: {alert['location']['ward']}\n"
            wa_message += f"🎯 Confidence: {alert['confidence']*100:.1f}%\n\n"
            wa_message += f"*RECOMMENDED ACTIONS:*\n"
            
            for action in alert['recommended_actions'][:3]:
                wa_message += f"• {action['action']}\n"
            
            wa_message += f"\nAlert ID: {alert['alert_id']}"
            
            for phone in recipients:
                self.twilio_client.messages.create(
                    body=wa_message,
                    from_=settings.TWILIO_WHATSAPP_FROM,
                    to=f"whatsapp:{phone}"
                )
                logger.info(f"WhatsApp sent to {phone}")
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {e}")
    
    async def _send_webhooks(self, webhooks: List[str], alert: dict):
        """Send webhook notifications"""
        try:
            async with httpx.AsyncClient() as client:
                for webhook_url in webhooks:
                    response = await client.post(
                        webhook_url,
                        json=alert,
                        timeout=10.0
                    )
                    logger.info(f"Webhook sent to {webhook_url}: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error sending webhooks: {e}")
    
    def _create_html_email(self, alert: dict) -> str:
        """Create HTML formatted email"""
        severity_colors = {
            "low": "#28a745",
            "medium": "#ffc107",
            "high": "#fd7e14",
            "critical": "#dc3545"
        }
        
        color = severity_colors.get(alert["severity"], "#6c757d")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: {color}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .metric {{ background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid {color}; }}
        .action {{ background-color: #fff3cd; padding: 10px; margin: 5px 0; border-left: 3px solid #ffc107; }}
        .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 DISEASE OUTBREAK ALERT</h1>
        <h2>{alert["severity"].upper()} SEVERITY</h2>
    </div>
    
    <div class="content">
        <h3>📍 Location: {alert["location"]["ward"]}</h3>
        <p><strong>Confidence:</strong> {alert["confidence"]*100:.1f}%</p>
        <p><strong>Anomaly Score:</strong> {alert["anomaly_score"]:.3f}</p>
        
        <h3>📊 Evidence Summary</h3>
        <div class="metric">
            <strong>Hospital Events:</strong> {alert["evidence"]["hospital"].get("total_events", "N/A")}
        </div>
        <div class="metric">
            <strong>Social Media Mentions:</strong> {alert["evidence"]["social"].get("total_mentions", "N/A")}
        </div>
        <div class="metric">
            <strong>Environmental Risk Score:</strong> {alert["evidence"]["environment"].get("risk_score", "N/A")}
        </div>
        
        <h3>💊 Recommended Actions</h3>
"""
        
        for action in alert["recommended_actions"]:
            html += f"""
        <div class="action">
            <strong>[{action["priority"].upper()}]</strong> {action["category"]}: {action["action"]}<br>
            <small>Target: {action["target"]}</small>
        </div>
"""
        
        html += f"""
    </div>
    
    <div class="footer">
        <p>Alert ID: {alert["alert_id"]} | Generated: {alert["timestamp"]}</p>
        <p>Silent Epidemic Detector (SED) System</p>
    </div>
</body>
</html>
"""
        return html


# Global notification service instance
notification_service = NotificationService()
