from allowed_requests import is_allowed_request


def handle_route(route):
    url = route.request.url

    if url.startswith("data:"):
        return route.continue_()

    if url.startswith("about:"):
        return route.continue_()

    if url.startswith("file:"):
        return route.abort()

    if is_allowed_request(url):
        return route.continue_()

    return route.abort()
