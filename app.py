from fastapi import FastAPI
from routers.flows import flows_router
from routers.webhooks import webhook_router
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.include_router(flows_router, prefix="/flow", tags=["Flows"])
app.include_router(webhook_router, prefix="/flow", tags=["Webhooks"])


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
