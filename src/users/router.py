from fastapi import APIRouter, Depends, status, Request, BackgroundTasks
from src.users import controller
from src.utils.db import get_db
from src.users import dtos
from sqlalchemy.orm import Session

user_routes = APIRouter(prefix="/users")

@user_routes.post("/register_user", status_code=status.HTTP_201_CREATED)
def register(body: dtos.UserSchema, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    return controller.register_user(body, db, background_tasks)

# --- NEW: Verify OTP Route ---
@user_routes.post("/verify_otp", status_code=status.HTTP_200_OK)
def verify_otp(body: dtos.VerifyOTPSchema, db: Session = Depends(get_db)):
    return controller.verify_user_otp(body, db)

@user_routes.post("/login", status_code=status.HTTP_200_OK)
def login(body: dtos.LoginSchema, db: Session = Depends(get_db)):
    return controller.user_login(body, db)

@user_routes.get("/is_auth", status_code=status.HTTP_200_OK, response_model=dtos.UserResponseSchema)
def is_auth(request: Request, db: Session = Depends(get_db)):
    return controller.is_authenticated(request, db)

@user_routes.post("/resend_otp", status_code=status.HTTP_200_OK)
def resend_otp(body: dtos.ForgotPasswordSchema, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    return controller.resend_verification_otp(body, db, background_tasks)

@user_routes.post("/forgot_password", status_code=status.HTTP_200_OK)
def forgot_password(body: dtos.ForgotPasswordSchema, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    return controller.forgot_password(body, db, background_tasks)

@user_routes.post("/reset_password", status_code=status.HTTP_200_OK)
def reset_password(body: dtos.ResetPasswordSchema, db: Session = Depends(get_db)):
    return controller.reset_password(body, db)