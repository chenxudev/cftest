from http_utils import json_response
from router import controller, route


@controller("/api/hello")
class HelloController:
    @route("GET")
    async def hello(self, request, env):
        return json_response({"status": "ok","data":"hello world"})