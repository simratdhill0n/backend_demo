from password_validator import PasswordValidator
from email_validator import validate_email, EmailNotValidError
import hashlib

  
def validate_password(password): 
    # Create a schema
    schema = PasswordValidator()

    # Add properties to it
    schema\
    .min(8)\
    .has().uppercase()\
    .has().lowercase()\
    .has().digits()\
    .has().no().spaces()\
    
    return schema.validate(password)
    
    

def check_email(email, check_deliverability=False):

    try:
        emailinfo = validate_email(email, check_deliverability=check_deliverability)
        return emailinfo.normalized

    except EmailNotValidError as e:

        return e
    
def create_secure_password(password):

    hash_object = hashlib.sha256()
    
    hash_object.update(password.encode())

    return hash_object.hexdigest()
