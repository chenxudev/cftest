async def list_items(db, limit, offset):
    result = await db.prepare(
        "SELECT id, name, description, created_at FROM items ORDER BY id LIMIT ? OFFSET ?"
    ).bind(limit, offset).all()
    return result.results


async def get_item(db, item_id):
    return await db.prepare(
        "SELECT id, name, description, created_at FROM items WHERE id = ?"
    ).bind(item_id).first()


async def create_item(db, name, description):
    return await db.prepare(
        "INSERT INTO items (name, description) VALUES (?, ?) "
        "RETURNING id, name, description, created_at"
    ).bind(name, description).first()


async def update_item(db, item_id, name, description):
    return await db.prepare(
        "UPDATE items SET name = ?, description = ? WHERE id = ? "
        "RETURNING id, name, description, created_at"
    ).bind(name, description, item_id).first()


async def delete_item(db, item_id):
    return await db.prepare(
        "DELETE FROM items WHERE id = ? RETURNING id"
    ).bind(item_id).first()
