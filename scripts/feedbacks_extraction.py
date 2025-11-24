import os
from pocketbase import PocketBase
import pandas as pd


email = "gcgbarbosa@gmail.com"
password = ",ofX2(0/5t*P"

server = os.getenv("POCKETBASE_URL", "")

db = PocketBase(server)
db.admins.auth_with_password(email, password)

feedback_records = db.collection("feedbacks").get_full_list()


output_data = []

for r in feedback_records:
    feedback_entry = r.feedback  # type: ignore

    feedback_entry["interaction_id"] = r.interaction_id  # type: ignore

    output_data.append(feedback_entry)

pd.DataFrame(output_data).to_excel("output.xlsx", index=False)
