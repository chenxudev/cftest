import json
from urllib.parse import parse_qs

from js import JSON
from workers import Response

MAX_SAFE_INTEGER = 9007199254740991


def json_response(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )


def from_js(value):
    return json.loads(JSON.stringify(value))


def parse_item_id(value):
    try:
        if not value.isascii() or not value.isdigit():
            raise ValueError
        item_id = int(value)
        if not 1 <= item_id <= MAX_SAFE_INTEGER:
            raise ValueError
        return item_id
    except ValueError:
        return None


def parse_pagination(query_string):
    query = parse_qs(query_string)
    try:
        limit = int(query.get("limit", ["20"])[0])
        offset = int(query.get("offset", ["0"])[0])
        if not 1 <= limit <= 100 or not 0 <= offset <= MAX_SAFE_INTEGER:
            raise ValueError
        return limit, offset
    except ValueError:
        return None


async def read_item(request):
    try:
        body = await request.text()
        if len(body) > 10000:
            return None, "Request body is too large"
        data = json.loads(body)
    except (ValueError, TypeError):
        return None, "Invalid JSON"

    if not isinstance(data, dict):
        return None, "Expected a JSON object"
    name = data.get("name")
    description = data.get("description", "")
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 200:
        return None, "name must contain 1 to 200 characters"
    if not isinstance(description, str) or len(description) > 2000:
        return None, "description must be a string of at most 2000 characters"
    return (name.strip(), description), None
