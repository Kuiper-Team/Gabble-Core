#I might implement rate limit and JWT too.
#And I can also switch the whole core to more professional frameworks and database management systems.
#I must add a concise permission system.
#The REST API must have a SQL injection attack prevention system.
import uvicorn
from fastapi import FastAPI, Request, responses
from pydantic import ValidationError

import api.presets as presets
from api.endpoints import home, channels, conversations, invites, messages, rooms, users

api = FastAPI(
    title="Gabble",
    responses={
        400: {
            "success": False,
            "error": "badrequest"
        },
        404: {
            "success": False,
            "error": "notfound"
        },
        405: {
            "success": False,
            "error": "methodnotallowed"
        },
        415: {
            "success": False,
            "error": "unsupportedmediatype"
        },
        500: {
            "success": False,
            "error": "internalservererror"
        }
    }
)

@api.exception_handler(ValidationError)
async def validation_handler(request: Request, exception: ValidationError):
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

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=443)