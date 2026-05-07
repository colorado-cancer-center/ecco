from fastapi import Request
from starlette.responses import Response

def request_key_builder(
    func,
    namespace: str = "",
    *,
    request: Request = None,
    response: Response = None,
    **kwargs,
) -> str:
    """
    This key builder builds a cache key based on the request method, path, and
    query parameters.
    
    This is to circumvent the default key builder's behavior of using the
    arguments to the method since in our case these are in-memory handles (like
    database sessions) that are newly created with each request, causing a cache
    miss every time.

    Lifted from the docs, https://github.com/long2ice/fastapi-cache?tab=readme-ov-file#custom-key-builder.
    """

    return ":".join(
        [
            namespace,
            (request.method.lower() if request else ""),
            (request.url.path if request else ""),
            repr(sorted(request.query_params.items())) if request else "",
        ]
    )
