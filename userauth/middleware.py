import re
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

logger = logging.getLogger(__name__)

class LoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log incoming requests, responses, and track the last visited page.
    """
    def process_request(self, request):
        """
        Logs incoming requests and saves the last visited GET page for redirection.
        """
        logger.info(f"Incoming request: {request.method} {request.path}")
        # Save the last visited non-POST (GET) page, excluding AJAX requests
        if request.method == 'GET' and not self._is_ajax(request):
            request.session['last_visited_page'] = request.path

    def _is_ajax(self, request):
        """
        Helper method to check if the request is an AJAX request.
        """
        return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def process_response(self, request, response):
        """
        Logs outgoing responses.
        """
        logger.info(f"Outgoing response: {response.status_code}")
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Logs the processing of a view.
        """
        logger.debug(f"Processing view: {view_func.__name__}")
        return None

    def process_exception(self, request, exception):
        """
        Logs exceptions.
        """
        logger.error(f"Exception occurred: {exception}")
        return None


class PreventBackButtonMiddleware(MiddlewareMixin):
    """
    Middleware to prevent browser back button issues, especially for edit pages.
    """
    def process_request(self, request):
        # Check if the request is for an edit page
        if re.search(r'/edit/\d+', request.path):  # Updated to match your URL structure
            # Set headers to prevent caching
            response = self.get_response(request)
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

            # Redirect users back to the dashboard if they try to access the edit page after saving
            if request.session.get('edit_completed', False):
                last_visited_page = request.session.get('last_visited_page', '/')
                return HttpResponseRedirect(last_visited_page)  # Replace 'dashboard' with your dashboard URL name

            return response

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called just before Django calls the view.
        """
        # Mark the session as completed if the user saves changes
        if request.method == 'POST' and re.search(r'/edit/\d+', request.path):  # Updated to match your URL structure
            request.session['edit_completed'] = True
        else:
            request.session['edit_completed'] = False

        return None