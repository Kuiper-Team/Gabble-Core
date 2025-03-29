alreadyamember = {
    "success": False,
    "error": "alreadyamember",
}, 401
incorrecthash = {
    "success": False,
    "error": "incorrecthash"
}, 401
invalidexpiry = {
    "success": False,
    "error": "invalidexpiry"
}, 406
invalidformat = {
    "success": False,
    "error": "invalidformat"
}, 406
invalidusername = {
    "success": False,
    "error": "invalidusername"
}, 406
missingparameter = {
    "success": False,
    "error": "missingparameter"
}, 406
nochannel = {
    "success": False,
    "error": "nochannel"
}, 406
nomessage = {
    "success": False,
    "error": "nomessage"
}, 406
noroom = {
    "success": False,
    "error": "noroom"
}, 406
nopermission = {
    "success": False,
    "error": "nopermission"
}, 403
nouser = {
    "success": False,
    "error": "nouser"
}, 406
userexists = {
    "success": False,
    "error": "userexists"
}, 406

success = { #Use along with a status code, either 200 or 201.
    "success": True
}
#Dictionary for Error Status Codes:
status_codes = {
    "alreadyamember": 401,
    "incorrecthash": 401,
    "invalidexpiry": 406,
    "invalidformat": 406,
    "invalidusername": 406,
    "missingarguments": 406,
    "nochannel": 406,
    "nomessage": 406,
    "noroom": 406,
    "nopermission": 403,
    "nouser": 406,
    "userexists": 406
}