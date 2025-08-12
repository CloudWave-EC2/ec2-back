# app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class SeatStatus(str, Enum):
    EMPTY = "EMPTY"
    HELD = "HELD"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class LoginReq(BaseModel):
    name: str
    password: str


class LoginRes(BaseModel):
    user_id: int
    name: str


class SeatOut(BaseModel):
    id: int
    code: str
    status: SeatStatus
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class HoldSeatsReq(BaseModel):
    member_id: int
    codes: List[str] = Field(..., min_items=1)


class ReservationReq(BaseModel):
    member_id: int
    codes: List[str] = Field(..., min_items=1)


class TicketOut(BaseModel):
    member_id: int
    seats: List[SeatOut] = []