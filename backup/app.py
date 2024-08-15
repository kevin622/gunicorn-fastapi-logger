import logging
import json

from fastapi import FastAPI, Request, Response

LOGGER_NAME = "debug_logger"

# Initialize FastAPI
app = FastAPI()


@app.middleware("http")
async def log_io(request: Request, call_next):
    # log request
    logger = logging.getLogger("my_logger")
    request_body = await request.body()
    logger.info(f"Request: {request.method} {request.url} {request.headers} {request_body}")

    # log response
    response = await call_next(request)
    res_body = b''
    async for chunk in response.body_iterator:
        res_body += chunk
    logger.info(f"Response: {response.status_code} {response.headers} {res_body}")

    return Response(
        content=res_body,
        status_code=response.status_code,
        headers=response.headers,
        media_type=response.media_type
    )


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
