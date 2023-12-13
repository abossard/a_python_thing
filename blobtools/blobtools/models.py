
from enum import Enum

from pydantic import BaseModel


class SagaStatus(str, Enum):
    pending = 'pending'
    completed = 'completed'
    
class Type(str, Enum):
    order = 'order'
    payment = 'payment'

class Saga(BaseModel):
    id: str
    type: Type
    status: SagaStatus = SagaStatus.pending
    ts: int

    def get_other_type(self):
        if self.type == Type.order:
            return Type.payment
        else:
            return Type.order

class SagaResult(BaseModel):
    sagas: list[Saga]
    order_location: str
    payment_location: str
