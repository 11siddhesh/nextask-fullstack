from fastapi import HTTPException, status, Request, Depends
from src.utils.settings import settings
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import jwt
from src.users.models import UserModel
from src.utils.db import get_db


# THis will work as dependcny fucntion 
def is_authenticated(request:Request,db:Session = Depends(get_db)):
    try:
        token =request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are UnAuthorized.")
        token = token.split(" ")[-1]
        # print(token)
        data = jwt.decode(token, settings.SECRET_KEY,settings.ALGORITHM)
        user_id = data.get("id")

        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are UnAuthorized.")
        return user
    # except InvalidTokenError:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are UnAuthorized.")
    except ExpiredSignatureError:
        # This will trigger exactly after your 10 seconds are up
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired. Please log in again.")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")