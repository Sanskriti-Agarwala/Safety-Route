def success_response(data, message="Success"):
    return {
        "success": True,
        "message": message,
        "data": data
    }

def error_response(message, status_code=500):
    return {
        "success": False,
        "message": message,
        "error_code": status_code
    }