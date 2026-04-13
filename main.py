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

@app.get("/wipe-db")
def wipe_db():
    db = SessionLocal()
    try:
        # This clears all users from the table immediately
        db.execute(text("TRUNCATE TABLE user_table CASCADE"))
        db.commit()
        return {"status": "success", "message": "Database wiped. You can now register again."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()