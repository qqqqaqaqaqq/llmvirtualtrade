# DB
from sqlalchemy import Column, BigInteger, Text, Numeric, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.sql import text

# 앱 내부
from app.db.base import Base

class UserInformation(Base):
    __tablename__ = "user_information"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="내부 식별자 Insert 순서 == 타임 테이블")
    
    userid = Column(Text, default="testuser", comment="유저 아이디")
    
    # 티커 플레이    
    play = Column(Boolean, default=False, comment="거래 실행")
    ticker = Column(JSONB, default=dict, comment="티커 허용")

    # 유저 프롬프트
    userprompt = Column(Text, comment="유저 프롬프트")
    
    # LLM API
    llm_model = Column(Text, comment="llm 모델")
    openai = Column(Text, comment="씨크릿 키")
    grok = Column(Text, comment="씨크릿 키")
    gemma = Column(Text, comment="씨크릿 키")

    # 거래소
    exchange = Column(Text, default="Upbit", comment="현재 거래소")

    # 거래 간격
    trade_interval = Column(BigInteger, default=86400, comment="거래 간격")

    # 수수료
    trading_fee = Column(Numeric, default=0.0, comment="거래소 수수료")

    start_time = Column(
        DateTime(timezone=True),
        server_default=text(
            "timezone('UTC', TIMESTAMP '2025-01-01 00:00:00')"
        ),
        comment="시작 시간 (UTC)"
    )

    end_time = Column(
        DateTime(timezone=True),
        server_default=text(
            "timezone('UTC', TIMESTAMP '2025-04-01 00:00:00')"
        ),
        comment="종료 시간 (UTC)"
    )