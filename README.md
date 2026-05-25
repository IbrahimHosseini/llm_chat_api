# LLM Chat API

A small FastAPI service that exposes a `/chat` endpoint backed by the OpenAI Chat Completions API.

The service keeps conversation history in memory by `session_id`, streams the model response internally, and supports a function tool for answering current-time questions by timezone.

## Features

- FastAPI application with a single chat endpoint.
- OpenAI `gpt-4.1-mini` chat completions integration.
- In-memory conversation history keyed by `session_id`.
- Retry handling for OpenAI rate-limit and 5xx API errors.
- Tool calling support with a built-in `get_current_time` tool.
- Environment-based configuration through `.env.local`.

## Project Structure

```text
.
├── app/
│   ├── main.py       # FastAPI app, OpenAI client, /chat endpoint
│   ├── schemas.py    # Pydantic request/message schemas
│   └── tools.py      # OpenAI tool definitions and local tool handlers
├── config.py         # Settings loaded from .env.local
├── requirements.txt  # Python dependencies
└── README.md
```

## Requirements

- Python 3.9 or newer
- OpenAI API key

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env.local` in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
```

## Run

Start the API with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API docs are available at:

```text
http://127.0.0.1:8000/docs
```

## API

### `POST /chat`

Send one or more chat messages for a session.

Request body:

```json
{
  "session_id": "demo-session",
  "messages": [
    {
      "role": "user",
      "content": "What time is it in Asia/Tehran?"
    }
  ]
}
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo-session",
    "messages": [
      {
        "role": "user",
        "content": "What time is it in Asia/Tehran?"
      }
    ]
  }'
```

Example response:

```text
The current time in Tehran is ...
```

## Request Schema

`session_id` is used to group messages into an in-memory conversation.

Each message must include:

| Field | Type | Allowed values |
| --- | --- | --- |
| `role` | string | `user`, `assistant`, `tool` |
| `content` | string | Message text |

## Tool Calling

The app registers one OpenAI function tool:

```text
get_current_time(timezone: string)
```

It uses Python's `zoneinfo` module, so timezone values should be valid IANA timezone names such as:

- `Asia/Tehran`
- `UTC`
- `America/New_York`
- `Europe/London`

## Notes

- Conversation history is stored in process memory and is lost when the server restarts.
- The current implementation does not persist users, sessions, or messages to a database.
- The API returns a plain string response from `/chat`, not a JSON envelope.

## License

MIT
