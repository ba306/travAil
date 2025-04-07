import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse, urlunparse, urlencode

logger = logging.getLogger(__name__)


def send_email(new_listings, sender_email, sender_password, receiver_email, search_params=None, search_id=None):
    subject = f"New Airbnb Listings Found{' with Search ID ' + str(search_id) if search_id else ''}"

    # Build the plain text email body
    text_body = "Search Parameters:\n"
    if search_params:
        text_body += f"- Dates: {search_params['start_date']} to {search_params['end_date']}\n"
        text_body += f"- Adults: {search_params['num_adults']}\n"
        text_body += f"- Max Price: €{search_params['max_price']}\n"
        if search_params.get('min_rating'):
            text_body += f"- Minimum Rating: {search_params['min_rating']}★\n"
        if search_params.get('min_reviews'):
            text_body += f"- Minimum Reviews: {search_params['min_reviews']}\n"
        text_body += f"- Location Bounds: NE({search_params['ne_lat']}, {search_params['ne_lng']}), SW({search_params['sw_lat']}, {search_params['sw_lng']})\n"

    text_body += "\nNew Listings:\n"
    if new_listings:
        for listing in new_listings:
            text_body += f"\nURL: {listing['short_url']}"
            text_body += f"\nPrice: {listing['price']}"
            if listing['rating']:
                text_body += f"\nRating: {listing['rating']}★"
            if listing['review_count']:
                text_body += f" ({listing['review_count']} reviews)"
            text_body += "\n"
    else:
        text_body += "No new listings found.\n"

    # Create MIME message
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # HTML version with table
    html_body = f"""
    <html>
        <body>
            <h2>Airbnb Search Results</h2>
            <h3>Search Parameters:</h3>
            <ul>
                <li><strong>Dates:</strong> {search_params['start_date']} to {search_params['end_date']}</li>
                <li><strong>Adults:</strong> {search_params['num_adults']}</li>
                <li><strong>Max Price:</strong> €{search_params['max_price']}</li>
                <li><strong>Location Bounds:</strong> NE({search_params['ne_lat']}, {search_params['ne_lng']}), SW({search_params['sw_lat']}, {search_params['sw_lng']})</li>
            </ul>

            <h3>New Listings:</h3>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th>Listing</th>
                        <th>Price</th>
                        <th>Rating</th>
                        <th>Reviews</th>
                    </tr>
                </thead>
                <tbody>
    """

    if new_listings:
        for listing in new_listings:
            rating_display = f"{listing['rating']}★" if listing['rating'] else "N/A"
            reviews_display = listing['review_count'] if listing['review_count'] else "N/A"

            html_body += f"""
                    <tr>
                        <td><a href="{listing['full_url']}" style="color: #0066cc; text-decoration: underline;">View Listing</a></td>
                        <td>{listing['price']}</td>
                        <td>{rating_display}</td>
                        <td>{reviews_display}</td>
                    </tr>
            """
    else:
        html_body += """
                    <tr>
                        <td colspan="4" style="text-align: center;">No new listings found</td>
                    </tr>
        """

    html_body += """
                </tbody>
            </table>
    """

    if search_id:
        termination_link = f"http://localhost:8000/terminate_search/{search_id}/"
        text_body += f"\nTo stop receiving updates for this search, click here: {termination_link}"
        html_body += f"""
            <p style="margin-top: 20px;">
                <a href="{termination_link}" style="color: #0066cc; text-decoration: underline;">Stop receiving updates for this search</a>
            </p>
        """

    html_body += """
        </body>
    </html>
    """

    # Attach both versions
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        logger.info(f"Email sent to {receiver_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
