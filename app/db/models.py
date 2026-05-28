from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    tax_code = Column(String(20), unique=True, index=True, nullable=True)
    business_code = Column(String(50), nullable=True)
    business_name = Column(String(255), index=True)
    normalized_business_name = Column(String(255), index=True)
    legal_representative = Column(String(255))
    normalized_legal_representative = Column(String(255))
    address = Column(String(500))
    normalized_address = Column(String(500))
    tax_authority = Column(String(255))
    status = Column(String(50))
    business_type = Column(String(100))
    industry = Column(String(255))
    phone = Column(String(50))
    email = Column(String(100))
    website = Column(String(255))
    issued_date = Column(Date)
    started_date = Column(Date)
    
    latest_source_name = Column(String(100))
    latest_source_url = Column(String(500))
    confidence_score = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_checked_at = Column(DateTime(timezone=True))
    
    sources = relationship("BusinessSource", back_populates="business")


class BusinessSource(Base):
    __tablename__ = "business_sources"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    tax_code = Column(String(20), index=True)
    source_name = Column(String(100))
    source_url = Column(String(500))
    crawled_at = Column(DateTime(timezone=True))
    
    raw_hash = Column(String(64))
    raw_payload = Column(JSON)
    parsed_payload = Column(JSON)
    
    confidence_score = Column(Float)
    error_message = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="sources")


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id = Column(Integer, primary_key=True, index=True)
    lookup_type = Column(String(20)) # tax_code or name
    lookup_value = Column(String(255))
    status = Column(String(50))
    provider_names = Column(JSON)
    
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    error_message = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
