# File: your_app/middleware.py

import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    """
    Middleware to log incoming requests and outgoing responses.
    """
    def __init__(self, get_response):
        """
        Initialize the middleware.
        :param get_response: The next middleware or view in the chain.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        This method is called for every request.
        :param request: The HttpRequest object.
        :return: The HttpResponse object.
        """
        # Log the incoming request
        logger.info(f"Incoming request: {request.method} {request.path}")

        response = self.get_response(request)

        # Log the outgoing response
        logger.info(f"Outgoing response: {response.status_code}")

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called just before Django calls the view.
        :param request: The HttpRequest object.
        :param view_func: The Python function that Django is about to use.
        :param view_args: Positional arguments for the view.
        :param view_kwargs: Keyword arguments for the view.
        :return: None or an HttpResponse object.
        """
        logger.debug(f"Processing view: {view_func.__name__}")
        return None  # Return None to continue processing, or return an HttpResponse to short-circuit.

    def process_exception(self, request, exception):
        """
        Called when a view raises an exception.
        :param request: The HttpRequest object.
        :param exception: The exception raised by the view.
        :return: None or an HttpResponse object.
        """
        logger.error(f"Exception occurred: {exception}")
        return None  # Return None to let Django handle the exception, or return an HttpResponse.