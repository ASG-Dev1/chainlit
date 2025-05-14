import chainlit as cl
from chainlit.config import config

# from chainlit.cosmos_history import save_message, get_user_messages
from cosmos_history import save_message, get_user_messages

# from cosmos_history import save_message, get_user_messages
import os
import uuid

print(f"ENABLE_AUTH: {os.getenv('ENABLE_AUTH')}")
print(f"TEST_USER_EMAIL: {os.getenv('TEST_USER_EMAIL')}")


from openai import AsyncAzureOpenAI


# Dev‑only test login: "admin" / "1234"
@cl.password_auth_callback
def login(username: str, password: str):
    class SimpleUser:
        def __init__(self, identifier, metadata=None):
            self.identifier = identifier
            self.metadata = metadata or {}

        def to_dict(self):
            return {"identifier": self.identifier, "metadata": self.metadata}

    if username == "admin" and password == "1234":
        return SimpleUser(identifier=username, metadata={"email": username})
    return None


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


@cl.on_chat_resume
async def on_resume(thread):
    user_id = cl.user_session.get("identifier", "anonymous")

    # Get the conversation ID from the resumed thread
    convo_id = thread["id"]
    messages = await get_user_messages(user_id, convo_id)

    for msg in messages:
        await cl.Message(author=msg["sender"], content=msg["content"]).send()


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
