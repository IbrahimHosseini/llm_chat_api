# app/main.py

import json
from pickle import NONE
from fastapi import FastAPI
from openai import AsyncOpenAI
from fastapi.responses import StreamingResponse
from config import settings
from .schemas import ChatRequest
from .tools import TOOLS, get_current_time

app = FastAPI()

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

@app.post("/chat")
async def chat(input: ChatRequest):
    messages = [m.model_dump() for m in input.messages]
    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        tools=TOOLS
    )

    if response.choices[0].finish_reason == "tool_calls":
        tool_call = response.choices[0].message.tool_calls[0]

        args = json.loads(tool_call.function.arguments)
        result = get_current_time(**args)

        messages.append(response.choices[0].message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })

        final = await client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=TOOLS
        )
        return final

    return response

    



    