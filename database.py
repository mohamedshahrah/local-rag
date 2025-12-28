from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import yaml

# Load Config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

Base = declarative_base()

class ChatMessage(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Setup DB
engine = create_engine(config['paths']['history_db'])
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def save_message(session_id, role, content):
    session = Session()
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    session.add(msg)
    session.commit()
    session.close()

def get_history(session_id, limit=10):
    session = Session()
    # Get last N messages for context
    messages = session.query(ChatMessage).filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
    session.close()
    return [{"role": m.role, "content": m.content} for m in messages]