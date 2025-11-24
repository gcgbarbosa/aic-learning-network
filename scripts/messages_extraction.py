import os
from pocketbase import PocketBase
import pandas as pd


email = "gcgbarbosa@gmail.com"
password = ",ofX2(0/5t*P"

server = os.getenv("POCKETBASE_URL", "")

db = PocketBase(server)
db.admins.auth_with_password(email, password)


def get_messages_from_chtbot(interaction_id: str) -> dict[str, list]:
    messages = db.collection("messages").get_full_list(
        query_params={"filter": f'interaction_id="{interaction_id}"', "expand": "chatbot_id"}
    )

    print(f"Total records: {len(messages)}")

    message_exchange = {
        "Chatbot 01": [],
        "Chatbot 02": [],
        "Chatbot 03": [],
    }
    for r in messages:
        chatbot = r.expand.get("chatbot_id")

        if chatbot:
            message_exchange[chatbot.name].append({"sender": "chatbot", "message": r.content, "timestamp": r.timestamp})
        else:
            for chatbot_name in message_exchange.keys():
                message_exchange[chatbot_name].append(
                    {"sender": "user", "message": r.content, "timestamp": r.timestamp}
                )

    return message_exchange


def create_excel_from_messages(message_exchange: dict[str, list], interaction_id: str) -> None:
    dfs = []

    for key, items in message_exchange.items():
        df = pd.DataFrame(items)
        dfs.append((key, df))

    # 'output.xlsx' is the name of the file you are creating
    with pd.ExcelWriter(f"data/chats/{interaction_id}.xlsx", engine="openpyxl") as writer:
        for key, df in dfs:
            df.to_excel(writer, sheet_name=key, index=False)


# chatbot_messages = get_messages_from_chtbot("7g4bc84ducsb6nx")
# create_excel_from_messages(chatbot_messages, "7g4bc84ducsb6nx")

df = pd.read_excel("learning-network-data.xlsx", sheet_name="Sheet1")

for interaction_id in df['interaction_id']:
    chatbot_messages = get_messages_from_chtbot(interaction_id)
    create_excel_from_messages(chatbot_messages, interaction_id)

    print(interaction_id)
    


