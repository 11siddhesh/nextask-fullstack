from src.users import dtos
from sqlalchemy.orm import Session
from src.users.models import UserModel
from fastapi import HTTPException, Request, status, BackgroundTasks
from pwdlib import PasswordHash
import jwt
from src.utils.settings import settings
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import smtplib
from email.mime.text import MIMEText
import random
import string
from src.utils.settings import settings

password_hash = PasswordHash.recommended()

def get_hash_password(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

# --- NEW: Email Sending Function ---
def send_otp_email(receiver_email: str, otp: str):
    sender_email = "YOUR_EMAIL@gmail.com" 
    sender_password = "YOUR_APP_PASSWORD" 

    msg = MIMEText(f"Your Task Manager verification code is: {otp}")
    msg['Subject'] = 'Verify your Account'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

# --- UPDATED: Register saves to DB as unverified ---
def register_user(body: dtos.UserSchema, db: Session, background_tasks: BackgroundTasks):
    is_user = db.query(UserModel).filter(UserModel.user_name == body.user_name).first()
    if is_user:
        raise HTTPException(400, detail="username already exists")
    
    is_user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if is_user:
        raise HTTPException(400, detail="email address already exists")
    
    hash_password = get_hash_password(body.password)
    
    # Generate 6-digit OTP and 10-minute expiry
    otp_code = ''.join(random.choices(string.digits, k=6))
    expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    new_user = UserModel(
        name=body.name,
        user_name=body.user_name,
        hash_password=hash_password,
        email=body.email,
        mobile_no=body.mobile_no,
        is_verified=False,  # Set default to unverified
        otp=otp_code,
        otp_exp=expiry
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send the email in the background
    background_tasks.add_task(send_otp_email, body.email, otp_code)

    return {"message": "OTP sent to your email. Please verify."}

# --- NEW: Verify the OTP against the DB ---
def verify_user_otp(body: dtos.VerifyOTPSchema, db: Session):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    
    if not user:
        raise HTTPException(404, detail="User not found.")
    if user.is_verified:
        raise HTTPException(400, detail="User is already verified.")
    if user.otp != body.otp:
        raise HTTPException(400, detail="Invalid OTP code.")
        
    # Ensure timezone info exists for comparison
    user_otp_exp = user.otp_exp.replace(tzinfo=timezone.utc) if user.otp_exp.tzinfo is None else user.otp_exp
    if datetime.now(timezone.utc) > user_otp_exp:
        raise HTTPException(400, detail="OTP has expired.")

    # Mark as verified and clean up OTP fields
    user.is_verified = True
    user.otp = None
    user.otp_exp = None
    
    db.commit()
    return {"message": "Account verified successfully! You can now log in."}

# --- UPDATED: Login (Blocks unverified users) ---
def user_login(body: dtos.LoginSchema, db: Session):
    user = db.query(UserModel).filter(UserModel.user_name == body.user_name).first()
    if not user:
        raise HTTPException(401, detail="wrong username")
    
    if not verify_password(body.password, user.hash_password):
        raise HTTPException(401, detail="wrong password")
        
    # Block login if not verified
    if not user.is_verified:
        raise HTTPException(403, detail="Please verify your email before logging in.")
        
    exp_time = datetime.now() + timedelta(minutes=settings.EXP_TIME)
    token = jwt.encode({"id": user.id, "exp": exp_time}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def is_authenticated(request: Request, db: Session):
    # ... (Keep your existing is_authenticated code exactly as it is) ...
    try:
        token = request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are UnAuthorized.")
        token = token.split(" ")[-1]
        data = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        user_id = data.get("id")

        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are UnAuthorized.")
        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired. Please log in again.")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    
def send_otp_email(receiver_email: str, otp: str):
    # --- UPDATE THESE TWO LINES ---
    sender_email = settings.EMAIL_SENDER
    sender_password = settings.EMAIL_PASSWORD

    msg = MIMEText(f"Your Task Manager verification code is: {otp}")
    msg['Subject'] = 'Verify your Account'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

def resend_verification_otp(body: dtos.ForgotPasswordSchema, db: Session, background_tasks: BackgroundTasks):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    
    if not user:
        raise HTTPException(404, detail="User not found.")
    if user.is_verified:
        raise HTTPException(400, detail="User is already verified. Please log in.")
        
    # Generate new OTP
    otp_code = ''.join(random.choices(string.digits, k=6))
    user.otp = otp_code
    user.otp_exp = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.commit()

    background_tasks.add_task(send_otp_email, body.email, otp_code)
    return {"message": "A new OTP has been sent to your email."}

def forgot_password(body: dtos.ForgotPasswordSchema, db: Session, background_tasks: BackgroundTasks):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not user:
        raise HTTPException(404, detail="If that email exists, an OTP has been sent.") # Vague message for security
        
    otp_code = ''.join(random.choices(string.digits, k=6))
    user.otp = otp_code
    user.otp_exp = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.commit()

    background_tasks.add_task(send_otp_email, body.email, otp_code)
    return {"message": "Password reset code sent to your email."}

def reset_password(body: dtos.ResetPasswordSchema, db: Session):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not user:
        raise HTTPException(404, detail="User not found.")
        
    if user.otp != body.otp:
        raise HTTPException(400, detail="Invalid OTP code.")
        
    user_otp_exp = user.otp_exp.replace(tzinfo=timezone.utc) if user.otp_exp.tzinfo is None else user.otp_exp
    if datetime.now(timezone.utc) > user_otp_exp:
        raise HTTPException(400, detail="OTP has expired.")

    # Hash new password and clear OTP
    user.hash_password = get_hash_password(body.new_password)
    user.otp = None
    user.otp_exp = None
    db.commit()
    
    return {"message": "Password has been reset successfully! You can now log in."}