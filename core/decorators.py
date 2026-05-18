import functools
import logging
import traceback
from rest_framework.response import Response

logger = logging.getLogger(__name__)


'''Customize decorator for api exception handling'''
def api_exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            
            #collent logg and trace
            logger.error(
                "Api Error occured",
                extra={
                    'error' : str(e),
                    'traceback' : traceback.format_exc()
                }
            )
            
            return Response(
                {
                    "success": False,
                    "message": "Internal server error"
                },
                status=500
            )

    return wrapper