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


def create_combined_excel_from_messages(message_exchange: dict[str, list], interaction_id: str) -> None:
    # 1. Prepare data for a single, combined DataFrame
    all_data = []

    # Assuming all lists (Chatbot 01, 02, 03) in message_exchange have the same length
    # due to how user messages are added to all of them.
    # We can iterate using the length of any of the lists, e.g., 'Chatbot 01'.
    
    # Get the names of the chatbots for easy access
    chatbot_names = list(message_exchange.keys())
    
    # Determine the number of message exchanges (turns)
    num_exchanges = len(message_exchange[chatbot_names[0]]) if chatbot_names else 0

    for i in range(num_exchanges):
        # The user message and timestamp are the same for all entries at index i
        user_entry = message_exchange[chatbot_names[0]][i]
        
        # Create a dictionary for the row
        row = {
            "Turn": i + 1,
            "User Message": user_entry.get("message"),
            "Timestamp": user_entry.get("timestamp"),
        }
        
        # Add the specific chatbot responses for this turn
        for name in chatbot_names:
            chatbot_entry = message_exchange[name][i]
            # We assume the 'sender' check is not strictly needed here 
            # because the list structure ensures alignment for turn 'i'.
            row[f"{name} Message"] = chatbot_entry.get("message")
            
        all_data.append(row)

    # 2. Create the combined DataFrame
    combined_df = pd.DataFrame(all_data)
    
    # 3. Write the single DataFrame to a single sheet
    output_filename = f"data/chats/{interaction_id}.xlsx"
    print(f"Writing combined chats to {output_filename}")
    
    # 'Combined Chats' is the name of the single sheet you are creating
    with pd.ExcelWriter(output_filename, engine="openpyxl") as writer:
        combined_df.to_excel(writer, sheet_name="Combined Chats", index=False)

# chatbot_messages = get_messages_from_chtbot("7g4bc84ducsb6nx")
# create_excel_from_messages(chatbot_messages, "7g4bc84ducsb6nx")

df = pd.read_excel("data/learning-network-data.xlsx", sheet_name="Sheet1")

for interaction_id in df['interaction_id']:
    chatbot_messages = get_messages_from_chtbot(interaction_id)

    # create_excel_from_messages(chatbot_messages, interaction_id)
    create_combined_excel_from_messages(chatbot_messages, interaction_id)

    print(interaction_id)
    


