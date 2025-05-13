import chainlit as cl
from chainlit.config import config
from cosmos_history import save_message, get_user_messages
import os
import uuid

from openai import AsyncAzureOpenAI

client = AsyncAzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("OPENAI_API_BASE"),
)


@cl.on_chat_start
async def start():
    user_id = cl.user_session.get("identifier", "anonymous")

    # Create a unique conversation ID per session
    conversation_id = str(uuid.uuid4())
    cl.user_session.set("conversation_id", conversation_id)

    await cl.Message(content=f"Hello {user_id}!").send()
    # messages = await get_user_messages(user_id, conversation_id)
    # for msg in messages:
    #     await cl.Message(author=msg["sender"], content=msg["content"]).send()


@cl.on_message
async def main(message: cl.Message):
    user_id = cl.user_session.get("identifier", "anonymous")
    conversation_id = cl.user_session.get("conversation_id")

    await save_message(user_id, message.content, "user", conversation_id)

    response = await client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_CHATGPT_MODEL", "chat"),
        messages=[{"role": "user", "content": message.content}],
        temperature=0.7,
    )

    reply = response.choices[0].message.content.strip()
    await save_message(user_id, reply, "assistant", conversation_id)
    await cl.Message(content=reply).send()
