# DB
from sqlalchemy import Column, BigInteger, Text, DateTime, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

# 앱 내부
from app.db.base import Base

class TradingHistory(Base):
    __tablename__ = "trading_history"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="내부 식별자 Insert 순서 == 타임 테이블")
    
    userid = Column(Text, default="testuser", comment="유저 아이디")
    
    createdtime = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 시간")

    why = Column(JSONB, comment="코인 포지션 사유")

    position = Column(JSONB, comment="코인 포지션")

    exchange = Column(Text, comment="거래소")

    trade_history = Column(JSONB, comment="거래 내역")

    available_cash = Column(Numeric, default=100000000, comment="사용 가능 현금")

    avg_list = Column(JSONB, comment="평균 단가 리스트")

    owner_coin = Column(JSONB, comment="보유 코인 리스트")

    total = Column(Numeric, default=100000000, comment="사용 가능 현금")