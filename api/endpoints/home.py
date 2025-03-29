from api.app import api

@api.route("/", methods=["GET", "POST"])
def home():
    return {
        "success": True,
        "reference_path": "/reference",
        "endpoints": {
            #(...)
        }
    }, 200

def reference():
    pass #(...)