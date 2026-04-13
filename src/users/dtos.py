from pydantic import BaseModel

class UserSchema(BaseModel):
    name: str
    user_name: str
    email: str
    password: str
    mobile_no: str
    
class UserResponseSchema(BaseModel):
    name: str
    user_name: str
    email: str

class LoginSchema(BaseModel):
    user_name: str
    password: str

class VerifyOTPSchema(BaseModel):
    email: str
    otp: str

class ForgotPasswordSchema(BaseModel):
    email: str

class ResetPasswordSchema(BaseModel):
    email: str
    otp: str
    new_password: str