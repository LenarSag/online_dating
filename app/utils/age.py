from datetime import date


def calculate_age(birthdate: date) -> int:
    today = date.today()
    # Calculate age based on year difference
    age = today.year - birthdate.year

    # Adjust if the birthday has not occurred this year yet
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1

    return age
