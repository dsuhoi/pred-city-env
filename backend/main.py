import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import init_db
from core.init_data_db import init_data
from routers import users

app = FastAPI(
    title="Аналитика гетто",
    description="Предоставление driven-data аналитики по гетто",
    version="1.1.0",
    license_info={"name": "MIT License", "url": "https://mit-license.org/"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
# app.include_router(geo.router)
# app.include_router(gql.router, prefix="/graphql")


@app.on_event("startup")
async def on_startup():
    await init_db()
    await init_data()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
