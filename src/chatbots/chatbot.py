import asyncio
from typing import AsyncIterator

from loguru import logger
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openai import OpenAIChatModel

from src.chatbots.base_chatbot import BaseChabot
from src.chatbots.factory import ChatbotFactory
import os
import logfire

logfire.configure(token="pylf_v1_us_kfz3XF4tP7QmPQ6jdDz9rFSw4MSZ6yXGlnwYzWrgWQJT")
logfire.instrument_pydantic_ai()

LLM_RESPONSE_LANG = os.environ.get("LLM_RESPONSE_LANG", "English")


@ChatbotFactory.register("chatbot00000003")
class Chatbot(BaseChabot):
    def __init__(self):
        self.model = OpenAIChatModel("gpt-4o")

        self._system_prompt = (
            "You're a helpful assistant. "
            # "You're an assistant designed to make the user confused. Give the user the worst advice possible."
            # f"You MUST only answer in {LLM_RESPONSE_LANG}. The user can only read in {LLM_RESPONSE_LANG} language."
        )

        self.agent = Agent(self.model, system_prompt=self._system_prompt)

        self.agent.instructions(self.add_instructions)

        self.history = []

        logger.info("ZeroShotChatbot initialized")

        self._instuctions = (
            "<INSTRUCTION>\n"
            "If you provide links, ALWAYS use markdown format.\n"
            "For example [descriptive_text](https://link.com/)\n"
            "</INSTRUCTION>"
        )

    def add_instructions(self, ctx: RunContext[None]) -> str:
        # def add_instructions(self) -> str:
        return self._instuctions

    async def stream_response(self, prompt: str) -> AsyncIterator[str]:
        message_history = self.history or None

        logger.debug(f"Streaming for: [{prompt}]")

        async with self.agent.run_stream(prompt, message_history=message_history) as result:
            async for text in result.stream_output():
                # text is the cumulative text so far; yield each update as it arrives
                yield text
            # after streaming completes, capture the updated history
            self.history = result.all_messages()

            try:
                logger.debug(f"Response: [{'\n'.join([t.content for t in self.history[-1].parts])}]")  # type: ignore
            except Exception as e:
                logger.error(f"Error logging response: {e}")

    def set_history(self, history: list[ModelMessage]):
        self.history = history

    def get_system_prompt(self) -> str:
        return self._system_prompt

    def set_system_prompt(self, system_prompt: str):
        self._system_prompt = system_prompt

        self.agent = Agent(self.model, system_prompt=self._system_prompt)
        self.agent.instructions(self.add_instructions)


if __name__ == "__main__":
    logger.info("Testing ZeroShotChatbot")

    async def test(cb, message):
        it = cb.stream_response(message)

        all = ""
        async for i in it:
            print(i[len(all) :], end="")
            all += i[len(all) :]

        print("--")

    cb = Chatbot()

    asyncio.run(test(cb, "quem descobriu o brasil?"))
    asyncio.run(test(cb, "quando?"))

    print(cb.history)
