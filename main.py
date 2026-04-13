from fastapi import FastAPI
from src.utils.db import Base,engine
# from src.tasks.models import TaskModel
from src.tasks.router import task_routes
from src.users.router import user_routes
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from src.utils.db import SessionLocal

# This line checks your database and creates any missing tables.
# Because your database is empty right now, it will just successfully connect!
Base.metadata.create_all(engine) #This line will be ont eime execute to only shck if db table exists or not

app = FastAPI(title = "This is Task Management App Portal")
app.include_router(task_routes)
app.include_router(user_routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/clean-my-email")
def clean_email():
    db = SessionLocal()
    try:
        # Replace 'your_email@gmail.com' with the email you want to delete
        email_to_delete = "11siddhesh10@gmail.com@gmail.com" 
        
        # This raw SQL will work on any DB
        query = text("DELETE FROM users WHERE email = :email")
        result = db.execute(query, {"email": email_to_delete})
        db.commit()
        
        return {"status": "success", "rows_deleted": result.rowcount}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()