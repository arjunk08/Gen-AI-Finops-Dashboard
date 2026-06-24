from db_end.db1 import Base
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class userid(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    invoices = relationship(
        "invoice",
        back_populates="userid"
    )

class invoice(Base):
    __tablename__="invoice_metadata"

    id=Column(Integer,primary_key=True,autoincrement=True)
    invoice_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    file_name=Column(String,nullable=False)
    file_hashid=Column(String,nullable=False)
    total_cost=Column(Integer)
    total_tokens=Column(Integer)
    row_count=Column(Integer)

    userid=relationship("userid",back_populates="invoices")

    rows=relationship("invoice_rows", back_populates="invoice")
    
    chat_history = relationship(
        "chathistory",
        back_populates="invoice"
    )

    optimization_rec = relationship(
        "optimization_rec",
        back_populates="invoice"
    )

class invoice_rows(Base):
    __tablename__="invoice_rows"
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoice_metadata.id"), nullable=False)

    billing_date = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    application = Column(String, nullable=True)
    team = Column(String, nullable=True)
    business_unit = Column(String,nullable=True)
    Model=Column(String,nullable=True)
    
    request_count = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    rate_usd = Column(Float, default=0)
    amount_usd = Column(Float, default=0)

    raw_data = Column(Text, nullable=True)
    chroma_id = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    invoice=relationship("invoice",back_populates="rows")


class chathistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoice_metadata.id"), nullable=False)

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    retrieved_context = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    invoice = relationship("invoice", back_populates="chat_history")


class optimization_rec(Base):
    __tablename__="optimization_rec"
    id =Column(Integer,nullable=False,primary_key=True)
    invoice_id=Column(Integer,ForeignKey("invoice_metadata.id"),nullable=False)
    steps=Column(String,nullable = True)
    created_at=Column(DateTime,server_default=func.now())

    invoice=relationship("invoice",back_populates="optimization_rec")

