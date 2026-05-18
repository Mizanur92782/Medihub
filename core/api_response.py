class APIResponse:

    @staticmethod
    def success(message="Data retrieved successfully", title="data", data=None):
        return {
            "success": True,
            "message": message,
            title: data if data is not None else "Data not provided in response"
        }

    @staticmethod
    def error(message="Error occurred in API response"):
        return {
            "success": False,
            "error": True,
            "message": message
        }