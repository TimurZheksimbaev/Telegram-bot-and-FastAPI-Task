from fastapi import FastAPI
from database.connect import init_db
from routers.user_router import user_router
from routers.admin_router import admin_router

app = FastAPI(on_startup=[init_db])
app.include_router(user_router)
app.include_router(admin_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
