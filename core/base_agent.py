from abc import ABC, abstractmethod
from typing import Dict, Any
from models import Message
import asyncio

class BaseAgent(ABC):
    def __init__(self, agent_id: str, broker):
        self.agent_id = agent_id
        self.broker = broker
        self.inbox: list[Message] = []
        self.state: Dict[str, Any] = {}
        
    async def setup(self):
        self.broker.subscribe(self.agent_id, self.receive_message)
        
    async def receive_message(self, message: Message):
        self.inbox.append(message)
        await self.process_message(message)
        
    @abstractmethod
    async def process_message(self, message: Message):
        pass
    
    async def send_message(self, receiver: str, msg_type: str, payload: Dict):
        msg = Message(sender=self.agent_id, receiver=receiver, message_type=msg_type, payload=payload)
        await self.broker.publish(msg)
        
    def get_state(self) -> Dict[str, Any]:
        return self.state.copy()
