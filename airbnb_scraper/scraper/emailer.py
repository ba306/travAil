import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(new_urls, sender_email, sender_password, receiver_email, search_params=None):
    subject = "New Airbnb Listings Found"

    # Format the email body with search parameters and listings
    body = "Search Parameters:\n"
    if search_params:
        body += f"- Dates: {search_params['start_date']} to {search_params['end_date']}\n"
        body += f"- Adults: {search_params['num_adults']}\n"
        body += f"- Max Price: €{search_params['max_price']}\n"
        body += f"- Location Bounds: NE({search_params['ne_lat']}, {search_params['ne_lng']}), SW({search_params['sw_lat']}, {search_params['sw_lng']})\n"

    body += "\nNew Listings:\n"
    if new_urls:
        body += "\n".join(new_urls)
    else:
        body += "No new listings found."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")