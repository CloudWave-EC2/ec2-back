from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from ..database import get_reader_db, get_writer_db
from ..models import User, Seat, SeatStatus
from ..schemas import (
    LoginReq, LoginRes,
    SeatOut, HoldSeatsReq,
    ReservationReq, TicketOut,
    SeatStatus as SeatStatusSchema,
)

api = APIRouter(prefix="/api", tags=["api"])


@api.post("/user/login", response_model=LoginRes, tags=["user"])
async def login(payload: LoginReq, db: AsyncSession = Depends(get_writer_db)):
    res = await db.execute(select(User).where(User.name == payload.name))
    user = res.scalar_one_or_none()
    if not user:
        user = User(name=payload.name, password=payload.password)
        db.add(user)
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            res = await db.execute(select(User).where(User.name == payload.name))
            user = res.scalar_one()
    return LoginRes(user_id=user.id, name=user.name)


@api.get("/members/{memberid}/ticket", response_model=TicketOut, tags=["members"])
async def get_member_ticket(memberid: int, db: AsyncSession = Depends(get_reader_db)):
    res = await db.execute(
        select(Seat).where(Seat.user_id == memberid, Seat.status == SeatStatus.CONFIRMED).order_by(Seat.code)
    )
    seats = res.scalars().all()
    return TicketOut(member_id=memberid, seats=seats)


@api.get("/seats", response_model=List[SeatOut], tags=["seats"])
async def list_seats(
    status: Optional[SeatStatusSchema] = Query(None, description="EMPTY/HELD/CONFIRMED/CANCELLED"),
    db: AsyncSession = Depends(get_reader_db),
):
    stmt = select(Seat)
    if status:
        stmt = stmt.where(Seat.status == SeatStatus(status.value))
    stmt = stmt.order_by(Seat.code)
    res = await db.execute(stmt)
    return res.scalars().all()


@api.post("/seats/hold", response_model=List[SeatOut], tags=["seats"])
async def hold_seats(payload: HoldSeatsReq, db: AsyncSession = Depends(get_writer_db)):
    ures = await db.execute(select(User).where(User.id == payload.member_id))
    if not ures.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Member not found")

    held: list[Seat] = []
    for code in payload.codes:
        sres = await db.execute(
            select(Seat).where(Seat.code == code).with_for_update(skip_locked=True)
        )
        seat = sres.scalar_one_or_none()
        if not seat:
            raise HTTPException(status_code=404, detail=f"Seat not found: {code}")
        if seat.status != SeatStatus.EMPTY:
            raise HTTPException(status_code=409, detail=f"Seat not available: {code} ({seat.status})")

        seat.status = SeatStatus.HELD
        seat.user_id = payload.member_id
        held.append(seat)

    return [SeatOut.model_validate(s) for s in held]


@api.post("/reservations", response_model=TicketOut, tags=["reservations"])
async def create_reservation(req: ReservationReq, db: AsyncSession = Depends(get_writer_db)):
    confirmed: list[Seat] = []
    for code in req.codes:
        sres = await db.execute(
            select(Seat).where(Seat.code == code).with_for_update(skip_locked=True)
        )
        seat = sres.scalar_one_or_none()
        if not seat:
            raise HTTPException(status_code=404, detail=f"Seat not found: {code}")
        if not (seat.status == SeatStatus.HELD and seat.user_id == req.member_id):
            raise HTTPException(status_code=409, detail=f"Seat not held by member or not HELD: {code}")

        seat.status = SeatStatus.CONFIRMED
        confirmed.append(seat)

    return TicketOut(member_id=req.member_id, seats=confirmed)