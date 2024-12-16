from fastapi import FastAPI, Response
from fastapi import HTTPException as FastApiHTTPException
from fastapi.requests import Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app_distribution_server.config import (
    APP_TITLE,
    APP_VERSION,
)
from app_distribution_server.errors import (
    UserError,
    status_codes_to_default_exception_types,
)
from app_distribution_server.routers import api_router, app_files_router, health_router, html_router

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    summary="Simple, self-hosted iOS/Android app distribution server.",
    description="[Source code, issues and documentation](https://github.com/significa/app-distribution-server)",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(api_router.router)
app.include_router(html_router.router)
app.include_router(app_files_router.router)
app.include_router(health_router.router)


@app.exception_handler(UserError)
async def exception_handler(
    request: Request,
    exception: FastApiHTTPException | StarletteHTTPException,
) -> Response:
    if request.url.path.startswith("/api/"):
        return PlainTextResponse(content=exception.detail)

    return await html_router.render_error_page(request, exception)


@app.exception_handler(StarletteHTTPException)
async def starlette_exception_handler(
    request: Request,
    exception: StarletteHTTPException,
) -> Response:
    filtered_exception = status_codes_to_default_exception_types.get(exception.status_code)
    if filtered_exception:
        return await exception_handler(request, filtered_exception())

    return await exception_handler(request, exception)
