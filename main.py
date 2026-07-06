import os
import httpx
from dotenv import load_dotenv

load_dotenv("/home/hermes/.hermes/.env")

NOTES_BASE_URL = os.getenv("NOTES_BASE_URL", "http://prof1cai.ru").rstrip("/")
MCP_TOKEN = os.getenv("NOTES_MCP_TOKEN", "")


def _notes_headers():
    if not MCP_TOKEN:
        raise RuntimeError("NOTES_MCP_TOKEN is not set in /home/hermes/.hermes/.env")
    return {
        "Authorization": f"Bearer {MCP_TOKEN}",
        "Content-Type": "application/json",
    }


def register(ctx):
    ctx.register_tool(
        name="notes_workspace_stats",
        toolset="notes",
        description="Проверка статуса workspace в сервисе заметок.",
        schema={
            "type": "object",
            "properties": {},
        },
        handler=notes_workspace_stats,
    )

    ctx.register_tool(
        name="notes_search",
        toolset="notes",
        description="Поиск заметок по тексту, типу, языку, тегу или entity_name.",
        schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "note_type": {"type": "string"},
                "language": {"type": "string"},
                "tag": {"type": "string"},
                "entity_name": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": [],
        },
        handler=notes_search,
    )

    ctx.register_tool(
        name="notes_get",
        toolset="notes",
        description="Получить заметку по id.",
        schema={
            "type": "object",
            "properties": {
                "note_id": {"type": "integer"},
            },
            "required": ["note_id"],
        },
        handler=notes_get,
    )

    ctx.register_tool(
        name="notes_create",
        toolset="notes",
        description="Создание новой заметки в сервисе заметок.",
        schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "note_type": {"type": "string", "default": "general"},
                "entity_name": {"type": "string"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "language": {"type": "string", "default": "ru"},
            },
            "required": ["title", "content"],
        },
        handler=notes_create,
    )

    ctx.register_tool(
        name="notes_update",
        toolset="notes",
        description="Обновление существующей заметки.",
        schema={
            "type": "object",
            "properties": {
                "note_id": {"type": "integer"},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "note_type": {"type": "string"},
                "entity_name": {"type": "string"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "language": {"type": "string"},
            },
            "required": ["note_id"],
        },
        handler=notes_update,
    )


async def notes_workspace_stats(payload: dict) -> dict:
    url = f"{NOTES_BASE_URL}/agent-api/workspace/stats"
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(url, headers=_notes_headers(), json={})
        resp.raise_for_status()
        return resp.json()


async def notes_search(payload: dict) -> dict:
    url = f"{NOTES_BASE_URL}/agent-api/notes/search"
    body = {}
    for key in ["query", "note_type", "language", "tag", "entity_name", "limit"]:
        value = payload.get(key)
        if value not in (None, "", []):
            body[key] = value

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, headers=_notes_headers(), json=body)
        resp.raise_for_status()
        return resp.json()


async def notes_get(payload: dict) -> dict:
    note_id = payload["note_id"]
    url = f"{NOTES_BASE_URL}/agent-api/notes/{note_id}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, headers=_notes_headers())
        resp.raise_for_status()
        return resp.json()


async def notes_create(payload: dict) -> dict:
    url = f"{NOTES_BASE_URL}/agent-api/notes"
    body = {
        "title": payload.get("title", "").strip(),
        "content": payload.get("content", ""),
        "note_type": payload.get("note_type", "general"),
        "entity_name": payload.get("entity_name") or None,
        "tags": payload.get("tags") or [],
        "language": payload.get("language", "ru"),
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, headers=_notes_headers(), json=body)
        resp.raise_for_status()
        return resp.json()


async def notes_update(payload: dict) -> dict:
    note_id = payload["note_id"]
    url = f"{NOTES_BASE_URL}/agent-api/notes/{note_id}"

    body = {}
    for key in ["title", "content", "note_type", "entity_name", "tags", "language"]:
        if key in payload and payload[key] is not None:
            body[key] = payload[key]

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.put(url, headers=_notes_headers(), json=body)
        resp.raise_for_status()
        return resp.json()
