# app/main.py

import json
import random
import asyncio
from fastapi import FastAPI
from openai import AsyncOpenAI, RateLimitError, APIStatusError
from config import settings
from .schemas import ChatRequest
from .tools import TOOLS, TOOL_MAP
from collections import defaultdict

app = FastAPI()

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

conversation_store = defaultdict(list)

@app.post("/chat")
async def chat(input: ChatRequest, max_retries: int = 3):

    history = conversation_store.get(input.session_id, [])

    messages = history + [m.model_dump() for m in input.messages]

    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                tools=TOOLS,
                stream=True
            )
            break
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait = (2 ** attempt) + random.uniform(0,1) #jitter
            await asyncio.sleep(wait) 

        except APIStatusError as e:
            if e.status_code >= 500:
                if attempt == max_retries - 1:
                    raise
                wait = (2 ** attempt) + random.uniform(0,1)
                await asyncio.sleep(wait)
            else:
                raise

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

    conversation_store[input.session_id].append(input.messages[-1].model_dump())

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
            final_content = final.choices[0].message.content

            assistant_message = {"role": "assistant", "content": final_content}
            conversation_store[input.session_id].append(assistant_message)

            return final_content

    user_content = {"role": "user", "content": content}
    conversation_store[input.session_id].append(user_content)
    return content
