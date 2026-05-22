# app/main.py

import json
from fastapi import FastAPI
from openai import AsyncOpenAI
from config import settings
from .schemas import ChatRequest
from .tools import TOOLS, TOOL_MAP

app = FastAPI()

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

@app.post("/chat")
async def chat(input: ChatRequest):
    messages = [m.model_dump() for m in input.messages]
    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        tools=TOOLS,
        stream=True
    )

    arguments = ""
    content = ""
    tool_call_id = None
    tool_name = None

    async for chunk in response:
        delta = chunk.choices[0].delta

        if delta.content is not None:
                content += delta.content

        if delta.tool_calls is not None:

            if delta.tool_calls[0].id is not None:
                tool_call_id = delta.tool_calls[0].id
            
            if delta.tool_calls[0].function.name is not None:
                tool_name = delta.tool_calls[0].function.name

            argument = delta.tool_calls[0].function.arguments
            arguments += argument

    if tool_name is not None:
        
        if tool_call_id is not None:

            args = json.loads(arguments)
            result = TOOL_MAP[tool_name](**args)

            messages.append({
                "role": "assistant",
                "tool_calls": [{
                    "id": tool_call_id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(result)
            })

            final = await client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                tools=TOOLS
            )
            return final.choices[0].message.content

    return content

    



    