from typing import Any
from .engine import InferenceEngine
from .types import Role, Message


class BaseAgent:
    """Базовый агент."""

    agent_id: str
    accepts_tools: bool = False

    def __init__(
        self,
        engine: InferenceEngine,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> None:
        self._engine = engine
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

    def build_messages(
        self,
        input: str,
        system_prompt: str | None = None
    ) -> list[Message]:
        """Собирает сообщения для формирования вызова."""
        messages: list[Message] = []
        if system_prompt:
            messages.append(Message(role=Role.SYSTEM, content=system_prompt))
        # if context and context.conversation.messages:
        #     messages.extend(context.conversation.messages)
        messages.append(Message(role=Role.USER, content=input))
        return messages

    def generate(self, messages: list[Message], **extra_kwargs: Any) -> dict:
        return self._engine.generate(
            messages,
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            **extra_kwargs,
        )
