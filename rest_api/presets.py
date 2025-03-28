alreadyamember = { #401
    "success": False,
    "error": "alreadyamember",
}
incorrecthash = { #401
    "success": False,
    "error": "incorrecthash"
}
incorrectpassword = { #401
    "success": False,
    "error": "incorrectpassword"
}
invalidexpiry = { #406
    "success": False,
    "error": "invalidexpiry"
}
invalidformat = { #406
    "success": False,
    "error": "invalidformat"
}
invalidusername = { #406
    "success": False,
    "error": "invalidusername"
}
missingarguments = { #406
    "success": False,
    "error": "missingargument"
}
nochannel = { #406
    "success": False,
    "error": "nochannel"
}
nomessage = { #406
    "success": False,
    "error": "nomessage"
}
noroom = { #406
    "success": False,
    "error": "noroom"
}
nopermission = { #403
    "success": False,
    "error": "nopermission"
}
nouser = { #406
    "success": False,
    "error": "nouser"
}
success_200 = { #200
    "success": True
}
success_201 = { #201
    "success": True
}

#Dictionary Storing Status Codes:
status_codes = {
    "alreadyamember": 401,
    "incorrecthash": 401,
    "incorrectpassword": 401,
    "invalidexpiry": 406,
    "invalidformat": 406,
    "invalidusername": 406,
    "missingarguments": 406,
    "nochannel": 406,
    "nomessage": 406,
    "noroom": 406,
    "nopermission": 403,
    "nouser": 406,
    "success": 200, #200 is preferred over 201 here.
}