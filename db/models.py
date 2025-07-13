from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func


Base = declarative_base()

class MasterDocs(Base):
    __tablename__="master_docs"
    
    id = Column(UUID(as_uuid=True),primary_key=True,server_default=func.gen_random_uuid(),index=True)
    path = Column(String)
    type = Column(Integer,default=0)
    is_active = Column(Boolean, default = True)
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    
    def __repr__(self):
        return f"<MasterDocs(id='{self.id}',path='{self.path}',type={self.type},is_active={self.is_active})>"