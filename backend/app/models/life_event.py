from sqlalchemy import Column, String, Integer, Text, DateTime, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class LifeEvent(Base):
    __tablename__ = "life_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_year = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    location_name = Column(String(255))
    latitude = Column(Float)  # Separate columns for SQLite compatibility
    longitude = Column(Float)  # Separate columns for SQLite compatibility
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def coordinates(self):
        """Return coordinates as tuple for compatibility"""
        if self.latitude and self.longitude:
            return (self.latitude, self.longitude)
        return None
    
    @coordinates.setter
    def coordinates(self, value):
        """Set coordinates from tuple"""
        if value and len(value) == 2:
            self.latitude, self.longitude = value
        else:
            self.latitude = None
            self.longitude = None
    
    def __repr__(self):
        return f"<LifeEvent(id={self.id}, title={self.title}, year={self.event_year})>"
