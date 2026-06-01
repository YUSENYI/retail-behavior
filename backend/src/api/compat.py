from __future__ import annotations

try:
    from fastapi import APIRouter, FastAPI, HTTPException
except ModuleNotFoundError:

    class APIRouter:  # type: ignore[no-redef]
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.routes: list[object] = []

        def get(self, *args: object, **kwargs: object):
            def decorator(func):
                self.routes.append(func)
                return func

            return decorator

        def post(self, *args: object, **kwargs: object):
            return self.get(*args, **kwargs)

        def patch(self, *args: object, **kwargs: object):
            return self.get(*args, **kwargs)

    class FastAPI:  # type: ignore[no-redef]
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.routers: list[APIRouter] = []

        def include_router(self, router: APIRouter, *args: object, **kwargs: object) -> None:
            self.routers.append(router)

    class HTTPException(Exception):  # type: ignore[no-redef]
        def __init__(self, status_code: int, detail: str) -> None:
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail
