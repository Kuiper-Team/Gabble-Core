#I might implement rate limit and JWT too.
#I can use Kafka instead of the database based inbox system.
#I must add a concise permission system.
from fastapi import FastAPI, HTTPException, Request, responses
from pydantic import ValidationError

import api.presets as presets
from api.endpoints import home, channels, conversations, invites, messages, rooms, users

api = FastAPI(
    title="Gabble",
    version="1.0.0"
)

@api.exception_handler(500)
async def error_500(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "internalservererror"
        }
    )

@api.exception_handler(400)
async def error_400(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "badrequest"
        }
    )

@api.exception_handler(401)
async def error_401(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=401,
        content={
            "success": False,
            "error": "unauthorized"
        }
    )

@api.exception_handler(403)
async def error_403(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=403,
        content={
            "success": False,
            "error": "forbidden"
        }
    )

@api.exception_handler(404)
async def error_404(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "notfound"
        }
    )

@api.exception_handler(405)
async def error_405(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=405,
        content={
            "success": False,
            "error": "methodnotallowed"
        }
    )

@api.exception_handler(415)
async def error_415(request: Request, exception: HTTPException):
    return responses.JSONResponse(
        status_code=415,
        content={
            "success": False,
            "error": "unsupportedmediatype"
        }
    )

@api.exception_handler(ValidationError)
async def validation_error(request: Request, exception: ValidationError):
    return responses.JSONResponse(
        status_code=422,
        content=presets.invalidformat
    )

api.include_router(home.router)
api.include_router(channels.router)
api.include_router(conversations.router)
api.include_router(invites.router)
api.include_router(messages.router)
api.include_router(rooms.router)
api.include_router(users.router)
