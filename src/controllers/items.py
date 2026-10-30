from urllib.parse import urlparse

from workers import Response

import items_repository as repository
from http_utils import from_js, json_response, parse_item_id, parse_pagination, read_item
from router import controller, route


@controller("/api/items")
class ItemsController:
    @route("GET")
    async def list_items(self, request, env):
        pagination = parse_pagination(urlparse(request.url).query)
        if pagination is None:
            return json_response(
                {"error": "limit must be between 1 and 100; offset must be non-negative"},
                400,
            )
        limit, offset = pagination
        rows = await repository.list_items(env.DB, limit, offset)
        return json_response({"items": from_js(rows), "limit": limit, "offset": offset})

    @route("POST")
    async def create_item(self, request, env):
        item, error = await read_item(request)
        if error:
            return json_response({"error": error}, 400)
        row = await repository.create_item(env.DB, *item)
        return json_response({"item": from_js(row)}, 201)

    @route("GET", "/{item_id}")
    async def get_item(self, request, env, item_id):
        item_id = parse_item_id(item_id)
        if item_id is None:
            return json_response({"error": "Invalid item id"}, 400)
        row = await repository.get_item(env.DB, item_id)
        if row is None:
            return json_response({"error": "Item not found"}, 404)
        return json_response({"item": from_js(row)})

    @route("PUT", "/{item_id}")
    async def update_item(self, request, env, item_id):
        item_id = parse_item_id(item_id)
        if item_id is None:
            return json_response({"error": "Invalid item id"}, 400)
        item, error = await read_item(request)
        if error:
            return json_response({"error": error}, 400)
        row = await repository.update_item(env.DB, item_id, *item)
        if row is None:
            return json_response({"error": "Item not found"}, 404)
        return json_response({"item": from_js(row)})

    @route("DELETE", "/{item_id}")
    async def delete_item(self, request, env, item_id):
        item_id = parse_item_id(item_id)
        if item_id is None:
            return json_response({"error": "Invalid item id"}, 400)
        row = await repository.delete_item(env.DB, item_id)
        if row is None:
            return json_response({"error": "Item not found"}, 404)
        return Response(None, status=204)
