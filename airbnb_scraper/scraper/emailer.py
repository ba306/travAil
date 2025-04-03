import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def send_email(new_urls, sender_email, sender_password, receiver_email, search_params=None, search_id=None):
    subject = "New Airbnb Listings Found"

    # Build the email body
    body = "Search Parameters:\n"
    if search_params:
        body += f"- Dates: {search_params['start_date']} to {search_params['end_date']}\n"
        body += f"- Adults: {search_params['num_adults']}\n"
        body += f"- Max Price: €{search_params['max_price']}\n"
        body += f"- Location Bounds: NE({search_params['ne_lat']}, {search_params['ne_lng']}), SW({search_params['sw_lat']}, {search_params['sw_lng']})\n"

    body += "\nNew Listings:\n"
    if new_urls:
        body += "\n".join(new_urls) + "\n"
    else:
        body += "No new listings found.\n"

    # Create MIME message
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Plain text version (shows full URL)
    text_body = body
    if search_id:
        termination_link = f"http://localhost:8000/terminate_search/{search_id}/"
        text_body += f"\nTo stop receiving updates for this search, click here: {termination_link}"

    # HTML version (hides URL behind "click here")
    html_body = body.replace('\n', '<br>')
    if search_id:
        html_body += f'<br><br>To stop receiving updates for this search, <a href="{termination_link}" style="color: #0066cc; text-decoration: underline;">click here</a>'

    # Attach both versions
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(f"<html><body>{html_body}</body></html>", 'html'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        logger.info(f"Email sent to {receiver_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")