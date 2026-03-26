from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class Gallery(Base):
    __tablename__ = "gallery"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("life_events.id"), nullable=True)
    media_url = Column(Text, nullable=False)
    caption = Column(Text)
    is_featured = Column(Boolean, default=False)
    media_type = Column(String(50), default="image")  # 'image', 'video'
    title = Column(String(255))
    description = Column(Text)
    file_size = Column(Integer)  # in bytes
    width = Column(Integer)
    height = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    life_event = relationship("LifeEvent", backref="gallery_items")
    
    def __repr__(self):
        return f"<Gallery(id={self.id}, title={self.title}, type={self.media_type})>"
