from .base_chatbot import BaseChabot
from .chatbot import Chatbot
from .factory import ChatbotFactory
from .message_adapter import MessageAdapter

from src.pocketbase_db import PocketBaseDB

# from .fewshot import FewshotChatbot
# from .rag import RAGChatbot
# from .zeroshot import ZeroshotChatbot
# # from .watwat import WatWatChatbot
#
#
# __all__ = ["BaseChabot", "FewshotChatbot", "RAGChatbot", "ZeroshotChatbot"]
__all__ = ["BaseChabot", "Chatbot", "ChatbotFactory", "MessageAdapter"]


db = PocketBaseDB()
chatbots_list = db.list_chatbots()
ChatbotFactory.is_database_in_sync(chatbots_list)
