import os
from datetime import datetime

from pydantic import EmailStr

from app.models.user_model import User


def send_notification_about_match(email_to: EmailStr, matched_user: User) -> None:
    # Create a directory to store emails if it doesn't exist
    email_dir = 'app/media/sent_emails'

    if not os.path.exists(email_dir):
        os.makedirs(email_dir)

    # Generate a unique filename
    email_filename = email_to.replace('.', '_')
    filename = (
        f"Email_to_{email_filename}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    )

    # Write the email content to a file
    filepath = os.path.join(email_dir, filename)
    with open(filepath, 'w') as file:
        file.write(f'Subject: You matched with {matched_user.first_name}:\n\n')
        file.write(
            f'You matched with {matched_user.first_name}. '
            f'Email address to contact person is {matched_user.email}'
        )
