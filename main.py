from fastapi import FastAPI
from src.utils.db import Base,engine
# from src.tasks.models import TaskModel
from src.tasks.router import task_routes
from src.users.router import user_routes
from fastapi.middleware.cors import CORSMiddleware

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

from sqlalchemy import text
from src.utils.db import SessionLocal

@app.get("/force-delete-users")
def force_delete():
    db = SessionLocal()
    try:
        # LIST THE EMAILS YOU WANT TO DELETE HERE
        emails_to_delete = ["11siddhesh10@gmail.com", "11siddhesh.exp@gmail.com"] 
        
        total_deleted = 0
        for email in emails_to_delete:
            # Check both possible table names
            query1 = text("DELETE FROM user_table WHERE email = :email")
            query2 = text("DELETE FROM users WHERE email = :email")
            
            res1 = db.execute(query1, {"email": email})
            res2 = db.execute(query2, {"email": email})
            total_deleted += (res1.rowcount + res2.rowcount)
        
        db.commit()
        return {
            "status": "success", 
            "total_rows_deleted": total_deleted,
            "emails_processed": emails_to_delete
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()