#I might implement rate limit and JWT too.
#And I can also switch the whole core to more professional frameworks and database management systems.
#I must add a concise permission system.
#The REST API must have a SQL injection attack prevention system.
import uvicorn
from fastapi import FastAPI

api = FastAPI(
    title="Gabble",
    docs_url=None,
    openapi_url=None,
    redoc_url=None,
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

from api.endpoints import users

api.include_router(users.router)

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=443)