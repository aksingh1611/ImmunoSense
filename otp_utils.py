import random

# Function to generate OTP containing only numbers
def generate_numeric_otp(length=6):
    """Generate a random numeric OTP of given length(6)."""
    otp = ''.join(random.choices('0123456789', k=length))
    return otp

