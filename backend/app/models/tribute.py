from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class Tribute(Base):
    __tablename__ = "tributes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_name = Column(String(100), nullable=False)
    relation_to_deceased = Column(String(100))
    message = Column(Text, nullable=False)
    candle_lit = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)  # Moderation layer
    email = Column(String(255))  # For contact/verification
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Tribute(id={self.id}, author={self.author_name}, approved={self.approved})>"
