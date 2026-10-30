from http_utils import json_response
from router import controller, route


@controller("/api/health")
class HealthController:
    @route("GET")
    async def health(self, request, env):
        return json_response({"status": "ok"})
