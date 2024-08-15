import logging
import json

from fastapi import FastAPI, Request, Response

from utils.models import Item

LOGGER_NAME = "debug_logger"

# Initialize FastAPI
app = FastAPI()


@app.middleware("http")
async def log_io(request: Request, call_next):
    logger = logging.getLogger(LOGGER_NAME)
    
    # log request
    request_body = await request.body()
    try:
        request_body = json.loads(request_body.decode())
    except:
        request_body = request_body.decode()
    logger.info(f"Request: {request.method} {request.url} {request.headers} {request_body}")

    # log response
    response = await call_next(request)
    res_body = b''
    async for chunk in response.body_iterator:
        res_body += chunk
    logger.info(f"Response: {response.status_code} {response.headers} {res_body.decode()}")

    return Response(
        content=res_body,
        status_code=response.status_code,
        headers=response.headers,
        media_type=response.media_type
    )


@app.get("/")
async def get_home():
    return {"message": "Hello, World!"}

@app.post("/")
async def post_home(item: Item):
    logger = logging.getLogger(LOGGER_NAME)
    response = {"message": "Unknown Error"}
    try:
        request_body = item.model_dump_json()
        logger.debug(f"Doing some process with request: {json.dumps(request_body)}")
        response["message"] = f"Finished without errors."
    except Exception as e:
        logger.exception(f"EXCEPTION OCCURED: {e}")
        response["message"] = f"Exception occured. Check logs."
    return response