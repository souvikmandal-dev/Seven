import anthropic
from dotenv import load_dotenv
import json
import os

load_dotenv()

client = anthropic.Anthropic()

MODEL = "claude-sonnet-5"
MAX_MEMORY_MESSAGES = 20

MEMORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "memory.json"
)


class Brain:
    def __init__(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as file:
                    self.messages = json.load(file)
            except Exception:
                self.messages = []
        else:
            self.messages = []

    def save_memory(self):
        with open(MEMORY_FILE, "w") as file:
            json.dump(self.messages, file, indent=4)

    def talk(self, user_input):
        try:
            self.messages.append({
                "role": "user",
                "content": user_input
            })

            self.messages = self.messages[-MAX_MEMORY_MESSAGES:]

            message = client.messages.create(
                model=MODEL,
                max_tokens=150,
                system=(
                    "You are Seven, a professional personal AI assistant. "
                    "Your creator is Souvik Mandal. "
                    "Address Souvik as Master when appropriate. "
                    "Be concise, intelligent, calm, and helpful."
                ),
                messages=self.messages
            )

            response = "".join(
                block.text for block in message.content
                if hasattr(block, "text")
            )

            self.messages.append({
                "role": "assistant",
                "content": response
            })

            self.messages = self.messages[-MAX_MEMORY_MESSAGES:]

            self.save_memory()

            return f"Seven: {response}"

        except Exception as error:
            return f"Seven: Error connecting to my AI brain: {error}"