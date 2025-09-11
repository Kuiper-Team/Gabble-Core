from fastapi import responses

def auto(code):
    return responses.JSONResponse(
        status_code=response_code[code],
        content={
            "success": False,
            "error": code
        }
    )

success = responses.JSONResponse(
    status_code=200,
    content={
        "success": True
    }
)
alreadyamember = responses.JSONResponse(
    status_code=401,
    content={
        "success": False,
        "error": "alreadyamember"
    }
)
alreadyfriends = responses.JSONResponse(
    status_code=401,
    content={
        "success": False,
        "error": "alreadyfriends"
    }
)
channelexists = responses.JSONResponse(
    status_code=406,
    content={
        "success": False,
        "error": "channelexists"
    }
)
incorrectpassword = responses.JSONResponse(
    status_code=401,
    headers={"WWW-Authenticate": "Bearer"},
    content={
        "success": False,
        "error": "incorrectcredentials"
    }
)
incorrecthash = responses.JSONResponse(
    status_code=401,
    content={
        "success": False,
        "error": "incorrecthash"
    }
)
incorrectpasscode = responses.JSONResponse(
    status_code=401,
    content={
        "success": False,
        "error": "incorrectpasscode"
    }
)
incorrectprivatekey = responses.JSONResponse(
    status_code=401,
    content={
        "success": False,
        "error": "incorrectprivatekey"
    }
)
invalidexpiry = responses.JSONResponse(
    status_code=422,
    content={
        "success": False,
        "error": "invalidexpiry"
    }
)
invalidformat = responses.JSONResponse(
    status_code=422,
    content={
        "success": False,
        "error": "invalidformat"
    }
)
inviteexpired = responses.JSONResponse(
    status_code=406,
    content={
        "success": False,
        "error": "inviteexpired"
    }
)
nochannel = responses.JSONResponse(
    status_code=404,
    content={
        "success": False,
        "error": "nochannel"
    }
)
noconversation = responses.JSONResponse(
    status_code=404,
    content={
        "success": False,
        "error": "noconversation"
    }
)
nomember = responses.JSONResponse(
    status_code=404,  # Assuming a default for nomember as it's not in response_code, using a common "not found" type error.
    content={
        "success": False,
        "error": "nomember"
    }
)
nomessage = responses.JSONResponse(
    status_code=404,
    content={
        "success": False,
        "error": "nomessage"
    }
)
noroom = responses.JSONResponse(
    status_code=404,
    content={
        "success": False,
        "error": "noroom"
    }
)
nopermission = responses.JSONResponse(
    status_code=403,
    content={
        "success": False,
        "error": "nopermission"
    }
)
notaninvitee = responses.JSONResponse(
    status_code=406,
    content={
        "success": False,
        "error": "notaninvitee"
    }
)
nottheinviter = responses.JSONResponse(
    status_code=406,
    content={
        "success": False,
        "error": "nottheinviter"
    }
)
nouser = responses.JSONResponse(
    status_code=406,
    content={
        "success": False,
        "error": "nouser"
    }
)
roomexists = responses.JSONResponse(
    status_code=406,
    content={
        "success": False,
        "error": "roomexists"
    }
)
sameasprevious = responses.JSONResponse(
    status_code=406,
    content={
        "success": False,
        "error": "sameasprevious",
    }
)
userexists = responses.JSONResponse(
    status_code=406,
    content={
        "success": False,
        "error": "userexists"
    }
)

response_code = {
    "success": 200,
    "alreadyamember": 401,
    "alreadyfriends": 401,
    "channelexists": 406,
    "incorrecthash": 401,
    "incorrectpasscode": 401,
    "incorrectprivatekey": 401,
    "invalidexpiry": 422,
    "invalidformat": 422,
    "inviteexpired": 406,
    "nochannel": 404,
    "noconversation": 404,
    "nomessage": 404,
    "noroom": 404,
    "nopermission": 403,
    "notaninvitee": 406,
    "nottheinviter": 406,
    "nouser": 406,
    "roomexists": 406,
    "sameasprevious": 406,
    "userexists": 406
}