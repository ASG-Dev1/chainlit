import os
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import (
    CosmosResourceNotFoundError,
    CosmosResourceExistsError,
)
from dotenv import load_dotenv

load_dotenv()

COSMOS_DB_URI = os.getenv("COSMOS_DB_URI")
COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")
COSMOS_DB_NAME = os.getenv("AZURE_DB_ID")
COSMOS_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

client = CosmosClient(COSMOS_DB_URI, COSMOS_DB_KEY)
database = client.get_database_client(COSMOS_DB_NAME)
container = database.get_container_client(COSMOS_CONTAINER_NAME)


async def save_message(user_id: str, message: str, sender: str, conversation_id: str):
    new_entry = {"sender": sender, "content": message}

    try:
        existing_item = await container.read_item(
            item=conversation_id,
            partition_key=conversation_id,  # <- assumes partitionKeyPath is "/id"
        )
        existing_item["messages"].append(new_entry)
        await container.replace_item(item=conversation_id, body=existing_item)

    except CosmosResourceNotFoundError:
        item = {
            "id": conversation_id,  # <- used as partition key
            "messages": [new_entry],
        }

        await container.create_item(body=item)


async def get_user_messages(user_id: str, conversation_id: str):
    try:
        query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
        result_iterable = container.query_items(query=query, partition_key=None)

        results = []
        async for item in result_iterable:
            results.append(item)

        return results

    except CosmosResourceNotFoundError:
        return []
