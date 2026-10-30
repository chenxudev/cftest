import importlib
import pkgutil
import re
from urllib.parse import urlparse

from http_utils import json_response


_routes = []


def _normalize(path):
    if not path.startswith("/"):
        raise ValueError("Route paths must start with '/'")
    return path.rstrip("/") or "/"


def _compile(path):
    parts = []
    names = set()
    specificity = []
    for segment in path.strip("/").split("/") if path != "/" else []:
        if segment.startswith("{") and segment.endswith("}"):
            name = segment[1:-1]
            if not name.isidentifier() or name in names:
                raise ValueError(f"Invalid path parameter: {segment}")
            names.add(name)
            parts.append(f"(?P<{name}>[^/]+)")
            specificity.append(0)
        else:
            if not segment or "{" in segment or "}" in segment:
                raise ValueError(f"Invalid route segment: {segment}")
            specificity.append(1)
            parts.append(re.escape(segment))
    expression = "/" + "/".join(parts)
    shape = re.sub(r"\(\?P<[^>]+>", "(", expression)
    return re.compile("^" + expression + "$"), shape, tuple(specificity)


def route(method, path="/"):
    method = method.upper()
    if not re.fullmatch(r"[A-Z]+", method):
        raise ValueError("Invalid HTTP method")
    _normalize(path)

    def decorate(function):
        if hasattr(function, "_route_definition"):
            raise ValueError("A method can have only one route")
        function._route_definition = (method, path)
        return function
    return decorate


def controller(prefix):
    prefix = _normalize(prefix)

    def decorate(cls):
        instance = cls()
        for function in vars(cls).values():
            definition = getattr(function, "_route_definition", None)
            if definition is None:
                continue
            method, suffix = definition
            full_path = _normalize(("" if prefix == "/" else prefix) + suffix)
            pattern, shape, specificity = _compile(full_path)
            if any(entry[0] == method and entry[2] == shape for entry in _routes):
                raise ValueError(f"Duplicate route: {method} {full_path}")
            _routes.append((method, pattern, shape, specificity, function.__get__(instance, cls)))
        _routes.sort(key=lambda entry: entry[3], reverse=True)
        return cls
    return decorate


def load_controllers():
    import controllers

    for module in pkgutil.iter_modules(controllers.__path__, controllers.__name__ + "."):
        if not module.ispkg:
            importlib.import_module(module.name)


async def dispatch(request, env):
    path = urlparse(request.url).path.rstrip("/") or "/"
    matches = [(entry, match) for entry in _routes if (match := entry[1].fullmatch(path))]
    if not matches:
        return json_response({"error": "Not found"}, 404)
    best = matches[0][0][3]
    for entry, match in matches:
        method, _, _, specificity, handler = entry
        if specificity == best and method == request.method:
            try:
                return await handler(request, env, **match.groupdict())
            except Exception as exc:
                print("Request failed:", exc)
                return json_response({"error": "Internal server error"}, 500)
    return json_response({"error": "Method not allowed"}, 405)
