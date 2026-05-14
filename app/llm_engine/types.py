"""Типы данных."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence  # noqa: I001


class Role(str, Enum):
    """Роли чат-сообщений."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Quantization(str, Enum):
    """Формат квантизации моделей."""

    NONE = "none"
    FP8 = "fp8"
    FP4 = "fp4"
    INT8 = "int8"
    INT4 = "int4"
    GGUF = "gguf"
    GGUF_Q4 = "gguf_q4"
    GGUF_Q8 = "gguf_q8"


class StepType(str, Enum):
    """Типы шагов в трассировке работы агента."""

    ROUTE = "route"
    RETRIEVE = "retrieve"
    GENERATE = "generate"
    TOOL_CALL = "tool_call"
    RESPOND = "respond"


# ----------------------------------------------------------------------------
# Типы сообщений
# ----------------------------------------------------------------------------


@dataclass(slots=True)
class ToolCall:
    """Простой запрос на вызов инструмента."""

    id: str
    name: str
    arguments: str  # JSON в виде строки


@dataclass(slots=True)
class Message:
    """Одиночное сообщение."""

    role: Role
    content: str = ""
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Conversation:
    """Сортированный лист сообщений."""

    messages: List[Message] = field(default_factory=list)
    max_messages: Optional[int] = None

    def add(self, message: Message) -> None:
        """Добавляет сообщение, отрезая старые."""
        self.messages.append(message)
        if (self.max_messages is not None and
           len(self.messages) > self.max_messages):
            self.messages = self.messages[-self.max_messages:]

    def window(self, n: int) -> List[Message]:
        """Возвращает последние N сообщений."""
        if n <= 0:
            return []
        return self.messages[-n:]


# ---------------------------------------------------------------------------
# Модель / tool / записи телеметрии
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class ModelSpec:
    """Метаданные LLM."""

    model_id: str
    name: str
    parameter_count_b: float
    context_length: int
    active_parameter_count_b: Optional[float] = None  # Активные параметры MoE
    quantization: Quantization = Quantization.NONE
    min_vram_gb: float = 0.0
    supported_engines: Sequence[str] = ()
    provider: str = ""
    requires_api_key: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ToolResult:
    """Возвращает результат вызова tool."""

    tool_name: str
    content: str
    success: bool = True
    usage: Dict[str, Any] = field(default_factory=dict)
    cost_usd: float = 0.0
    latency_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TelemetryRecord:
    """Запись телеметрической информации после вызова tool."""

    timestamp: float
    model_id: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_seconds: float = 0.0
    ttft: float = 0.0  # время до первого токена
    cost_usd: float = 0.0
    energy_joules: float = 0.0
    power_watts: float = 0.0
    gpu_utilization_pct: float = 0.0
    gpu_memory_used_gb: float = 0.0
    gpu_temperature_c: float = 0.0
    throughput_tok_per_sec: float = 0.0
    energy_per_output_token_joules: float = 0.0
    throughput_per_watt: float = 0.0
    prefill_latency_seconds: float = 0.0
    decode_latency_seconds: float = 0.0
    prefill_energy_joules: float = 0.0
    decode_energy_joules: float = 0.0
    mean_itl_ms: float = 0.0
    median_itl_ms: float = 0.0
    p90_itl_ms: float = 0.0
    p95_itl_ms: float = 0.0
    p99_itl_ms: float = 0.0
    std_itl_ms: float = 0.0
    is_streaming: bool = False
    engine: str = ""
    agent: str = ""
    energy_method: str = ""
    energy_vendor: str = ""
    batch_id: str = ""
    is_warmup: bool = False
    cpu_energy_joules: float = 0.0
    gpu_energy_joules: float = 0.0
    dram_energy_joules: float = 0.0
    tokens_per_joule: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Трассировка работы агента
# ---------------------------------------------------------------------------


def _trace_id() -> str:
    return uuid.uuid4().hex[:16]


@dataclass(slots=True)
class TraceStep:
    """Шаг трассипровки.

    Каждый шаг записывает что сделал агента (route, retrieve, generate,
    tool_call, respond), ввод, вывод.
    """

    step_type: StepType
    timestamp: float
    duration_seconds: float = 0.0
    input: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Trace:
    """Полная трассировка работы агента."""

    trace_id: str = field(default_factory=_trace_id)
    query: str = ""
    agent: str = ""
    model: str = ""
    engine: str = ""
    steps: List[TraceStep] = field(default_factory=list)
    result: str = ""
    outcome: Optional[str] = None  # None=unknown, "success", "failure"
    feedback: Optional[float] = None  # user quality score [0, 1]
    started_at: float = 0.0
    ended_at: float = 0.0
    total_tokens: int = 0
    total_latency_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_step(self, step: TraceStep) -> None:
        """Добавляет шаг."""
        self.steps.append(step)
        self.total_latency_seconds += step.duration_seconds
        self.total_tokens += step.output.get("tokens", 0)


@dataclass(slots=True)
class RoutingContext:
    """Контекст для маршрутизации агента."""

    query: str = ""
    query_length: int = 0
    has_code: bool = False
    has_math: bool = False
    language: str = "en"
    urgency: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


__all__ = [
    "Conversation",
    "Message",
    "ModelSpec",
    "Quantization",
    "Role",
    "RoutingContext",
    "StepType",
    "TelemetryRecord",
    "ToolCall",
    "ToolResult",
    "Trace",
    "TraceStep",
]
