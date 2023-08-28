import traceback

import uvicorn as uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI
from requests import Request
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from controller import (
    datastep_controller, chat_controller, message_controller,
    review_controller, mark_controller, auth_controller
)

load_dotenv()

app = FastAPI()

app.include_router(auth_controller.router)
app.include_router(datastep_controller.router)
app.include_router(chat_controller.router)
app.include_router(message_controller.router)
app.include_router(review_controller.router)
app.include_router(mark_controller.router)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={
                "message": f"{e}",
                "traceback": traceback.format_exception(e)
            },
        )

app = VersionedFastAPI(
    app,
    version_format='{major}',
    prefix_format='/api/v{major}',
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=[
                "https://msu-frontend.fly.dev",
                "https://msu-frontend-dev.fly.dev",
                "https://datastep-frontend-mock.fly.dev",
                "http://localhost:3000"
            ],
            allow_methods=["POST", "GET", "PUT", "DELETE"],
            allow_headers=["*"],
        )
    ]
)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=False)
