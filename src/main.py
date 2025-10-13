from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from srknote.api.auth import router as auth_router
from srknote.api.note import router as notes_router
from srknote.api.user import router as user_router

from srknote.config.base import Base
from srknote.config.db import get_engine

Base.metadata.create_all(bind=get_engine())

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth_router)
app.include_router(notes_router)

app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "API is running"}

# Health check route
@app.get("/health", tags=["health"])
async def health():
    return {"ok": True}


# Custom route for Swagger UI documentation
@app.get("/mc101docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="MC101 API Docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)