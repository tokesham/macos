from typing import Dict, List, Callable
from models import Message
import asyncio

class MessageBroker:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_history: List[Message] = []

    def subscribe(self, agent_id: str, callback: Callable):
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)

    def unsubscribe(self, agent_id: str, callback: Callable):
        if agent_id in self.subscribers:
            self.subscribers[agent_id].remove(callback)

    async def publish(self, message: Message):
        self.message_history.append(message)
        if message.receiver in self.subscribers:
            for callback in self.subscribers[message.receiver]:
                await callback(message)
        if "broadcast" in self.subscribers:
            for callback in self.subscribers["broadcast"]:
                await callback(message)

    def get_history(self, agent_id: str = None) -> List[Message]:
        if agent_id:
            return [m for m in self.message_history if m.receiver == agent_id or m.sender == agent_id]
        return self.message_history
