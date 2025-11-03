from pocketbase import PocketBase
import os

from pocketbase.models import Record
from pocketbase.stores.base_auth_store import BaseAuthStore

server = os.getenv("POCKETBASE_URL", "")

client = PocketBase(server)


login = client.collection("users").auth_with_password("test@test.com", "test@test")
# print(login)
print(login.record.__dict__)
# print(login.is_valid)
# print(login.meta)
# print(login.token)
#
# login = client.collection("users").auth_refresh()
# print(login)
# print(login.record.__dict__)
# print(login.is_valid)
# print(login.meta)
# print(login.token)


data = login.record.__dict__

data["updated"] = data["updated"].strftime("%Y-%m-%d %H:%M:%S")
data["created"] = data["created"].strftime("%Y-%m-%d %H:%M:%S")


k = Record(login.record.__dict__)
token = login.token


print(k.__dict__)

auth = BaseAuthStore(base_token=token, base_model=k)

client = PocketBase(server, auth_store=auth)


chatbots = client.collection("chatbots").get_full_list()

print(chatbots)

print(client.collection("users").auth_refresh().is_valid)
