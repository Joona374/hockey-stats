from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float



# Replace placeholders with your MySQL credentials
DATABASE_URL = "mysql+pymysql://username:password@localhost/your_database"

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Product(Base):
    __tablename__ = 'products'  # Table name in the database

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Float)
    description = Column(String(255))

    def __repr__(self):
        return f"<Product(name={self.name}, price={self.price})>"
    
Base.metadata.create_all(engine)