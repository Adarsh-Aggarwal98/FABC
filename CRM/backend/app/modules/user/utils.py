import secrets
import string
import os
from werkzeug.utils import secure_filename
from flask import current_app


def generate_password(length=12):
    """
    Generate a secure random password.
    Includes uppercase, lowercase, digits, and special characters.
    """
    # Ensure at least one of each character type
    uppercase = secrets.choice(string.ascii_uppercase)
    lowercase = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice('!@#$%^&*')

    # Fill the rest with random characters
    all_chars = string.ascii_letters + string.digits + '!@#$%^&*'
    remaining_length = length - 4
    remaining = ''.join(secrets.choice(all_chars) for _ in range(remaining_length))

    # Combine and shuffle
    password = uppercase + lowercase + digit + special + remaining
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)

    return ''.join(password_list)


def generate_otp(length=6):
    """Generate a numeric OTP"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, subfolder='documents'):
    """
    Save an uploaded file and return the relative path.
    """
    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        raise ValueError('File type not allowed')

    # Secure the filename
    filename = secure_filename(file.filename)

    # Add unique prefix to prevent collisions
    unique_filename = f"{secrets.token_hex(8)}_{filename}"

    # Create upload directory if it doesn't exist
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    target_folder = os.path.join(upload_folder, subfolder)
    os.makedirs(target_folder, exist_ok=True)

    # Save the file
    file_path = os.path.join(target_folder, unique_filename)
    file.save(file_path)

    # Return relative path for storage
    return f"{subfolder}/{unique_filename}"


def validate_password_strength(password):
    """
    Validate password meets minimum requirements.
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'

    if not any(c.isupper() for c in password):
        return False, 'Password must contain at least one uppercase letter'

    if not any(c.islower() for c in password):
        return False, 'Password must contain at least one lowercase letter'

    if not any(c.isdigit() for c in password):
        return False, 'Password must contain at least one digit'

    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        return False, 'Password must contain at least one special character'

    return True, None
