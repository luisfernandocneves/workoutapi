from fastapi import FastAPI
from routers import api_router

app = FastAPI(title="WorkoutAPI")
app.include_router(api_router)



#if __name__ == "main":
#    import uvicorn

#    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)

#@app.get("/")
#async def root():
#    return {"message": "Hello World"}