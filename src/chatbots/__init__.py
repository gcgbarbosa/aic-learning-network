from .base_chatbot import BaseChabot
from .chatbot import Chatbot
from .factory import ChatbotFactory

from src.pocketbase_db import PocketBaseDB

# from .fewshot import FewshotChatbot
# from .rag import RAGChatbot
# from .zeroshot import ZeroshotChatbot
# # from .watwat import WatWatChatbot
#
#
# __all__ = ["BaseChabot", "FewshotChatbot", "RAGChatbot", "ZeroshotChatbot"]
__all__ = ["BaseChabot", "Chatbot", "ChatbotFactory"]


db = PocketBaseDB()
chatbots_list = db.list_chatbots()
ChatbotFactory.is_database_in_sync(chatbots_list)
