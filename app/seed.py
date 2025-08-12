import asyncio
from sqlalchemy import select
from .database import engine, AsyncSessionLocal
from .models import Base, Seat, SeatStatus, User

async def seed():
    # DB와 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 기본 유저 생성 (없으면)
        user_res = await db.execute(select(User).where(User.name == "demo"))
        if not user_res.scalar_one_or_none():
            db.add(User(name="demo", password="1234"))  # 단순 저장(해시 X)

        # 좌석 데이터 생성 (없으면)
        seat_res = await db.execute(select(Seat).limit(1))
        if not seat_res.scalar_one_or_none():
            rows = ["A", "B", "C", "D"]
            for row in rows:
                for num in range(1, 13):
                    code = f"{row}{num}"
                    db.add(Seat(code=code, status=SeatStatus.EMPTY))
            print("Seats inserted: A1~D12")

        await db.commit()
        print("Seed data created: demo user + seats")

if __name__ == "__main__":
    asyncio.run(seed())
