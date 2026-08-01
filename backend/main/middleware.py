class NoStoreForAuthenticatedMiddleware:
    """Prevent browsers from caching authenticated pages.

    Without these headers the browser may keep authenticated pages in its
    back/forward cache, so after logout the user can press back and see the
    previous dashboard/profile without a fresh request. Marking them
    no-store forces the browser to fetch from the server again, where the
    destroyed session sends the user to the login page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
