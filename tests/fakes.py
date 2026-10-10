from __future__ import annotations

import importlib
import logging
import sys
import types
from dataclasses import dataclass, field
from unittest.mock import AsyncMock, patch


@dataclass
class Plain:
    text: str


@dataclass
class At:
    qq: str


@dataclass
class Reply:
    id: str


class Image:
    pass


@dataclass
class Conversation:
    cid: str = "conversation-1"
    persona_id: str = "当前人格"
    history: str = "[]"


@dataclass
class Request:
    prompt: str
    system_prompt: str = ""
    conversation: Conversation | None = None
    contexts: list = field(default_factory=list)


class FakeEvent:
    def __init__(
        self,
        text: str,
        *,
        group="100",
        sender="12345",
        self_id="99999",
        platform="qq",
        message=None,
    ):
        self.message = [Plain(text)] if message is None else message
        self.message_obj = types.SimpleNamespace(self_id=self_id)
        self.sender = sender
        self.platform = platform
        self.unified_msg_origin = f"{platform}:{group or 'private_' + sender}"
        self.stopped = False
        self.sent = []
        self.requests = []
        self.llm_enabled = True

    def get_messages(self):
        return self.message

    def get_sender_id(self):
        return self.sender

    def get_platform_id(self):
        return self.platform

    def stop_event(self):
        self.stopped = True

    def plain_result(self, text):
        return text

    async def send(self, result):
        self.sent.append(result)

    def request_llm(self, **kwargs):
        request = Request(**kwargs)
        self.requests.append(request)
        return request


class FakeContext:
    def __init__(self):
        self.config = {
            "provider_settings": {"enable": True},
            "agent_runner": {"runner_type": "local"},
        }
        self.conversation = Conversation()
        self.get_config = lambda umo: self.config
        self.get_current_chat_provider_id = AsyncMock(return_value="current-provider")
        self.conversation_manager = types.SimpleNamespace(
            get_curr_conversation_id=AsyncMock(return_value=self.conversation.cid),
            get_conversation=AsyncMock(return_value=self.conversation),
            new_conversation=AsyncMock(return_value="new-conversation"),
        )


def import_entry():
    api = types.ModuleType("astrbot.api")
    components = types.ModuleType("astrbot.api.message_components")
    for component in (Plain, At, Reply, Image):
        setattr(components, component.__name__, component)
    api.message_components = components
    api.AstrBotConfig = dict
    api.logger = logging.getLogger("1d-choice-tests")
    event = types.ModuleType("astrbot.api.event")
    event.AstrMessageEvent = FakeEvent
    event.filter = types.SimpleNamespace(
        EventMessageType=types.SimpleNamespace(ALL="all"),
        event_message_type=lambda *args, **kwargs: lambda function: function,
    )
    star = types.ModuleType("astrbot.api.star")

    class Star:
        def __init__(self, context):
            self.context = context

    star.Context, star.Star = FakeContext, Star
    session = types.ModuleType("astrbot.core.star.session_llm_manager")

    class SessionServiceManager:
        @staticmethod
        async def should_process_llm_request(event):
            return event.llm_enabled

    session.SessionServiceManager = SessionServiceManager
    modules = {
        "astrbot": types.ModuleType("astrbot"),
        "astrbot.api": api,
        "astrbot.api.event": event,
        "astrbot.api.star": star,
        "astrbot.api.message_components": components,
        "astrbot.core": types.ModuleType("astrbot.core"),
        "astrbot.core.star": types.ModuleType("astrbot.core.star"),
        "astrbot.core.star.session_llm_manager": session,
    }
    with patch.dict(sys.modules, modules):
        return importlib.import_module("astrbot_plugin_1d_choice.main")
