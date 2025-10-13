import logging
import time
import json
from pathlib import Path
from fastapi import Request, Response


def setup_logger():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)


    log_file=log_dir/f"log.log"

    loger = logging.getLogger("api_logger")
    loger.setLevel(logging.INFO)

    if not loger.handlers:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        )
        loger.addHandler(handler)

    return loger


logger = setup_logger()


def mask_sensitive_data(data: dict) -> dict:
    """Mask sensitive fields."""
    sensitive = {"password", "token", "secret", "api_key"}

    if isinstance(data, dict):
        return {
            k: "***MASKED***" if k.lower() in sensitive else v
            for k, v in data.items()
        }
    return data


async def log_requests(request: Request, call_next):
    """Middleware function to log requests and responses."""
    request_id = id(request)
    start_time = time.time()

    log_msg = f"[{request_id}] {request.method} {request.url.path}"

    if request.query_params:
        log_msg += f" | Query: {dict(request.query_params)}"

    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                body_json = json.loads(body.decode())
                body_json = mask_sensitive_data(body_json)
                log_msg += f" | Body: {json.dumps(body_json)}"
        except:
            pass

    logger.info(log_msg)

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        log_level = "error" if response.status_code >= 400 else "info"
        getattr(logger, log_level)(
            f"[{request_id}] Response: {response.status_code} | Time: {process_time:.4f}s"
        )

        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"[{request_id}] Failed after {process_time:.4f}s | Error: {str(e)}")
        raise