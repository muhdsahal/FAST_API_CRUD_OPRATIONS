from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy import create_engine,Column,Integer,String
import sqlalchemy
from sqlalchemy.orm import sessionmaker,Session
from pydantic import BaseModel
from typing import List

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = sqlalchemy.orm.declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,index=True)
    description = Column(String)

Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ItemCreate(BaseModel):
    name : str
    description : str


class ItemResponse(BaseModel):
    id : int
    name : str
    description :str


@app.post("/items/",response_model=ItemResponse)
async def create_item (item:ItemCreate,db:Session = Depends(get_db)):
    db_item = Item(**item.dict())
    print(db_item.name,db_item.id,'kkkkkkkkkkkkkkkkkkkkkkkkkkk')
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/",response_model=List[ItemResponse])
async def read_item(db:Session=Depends(get_db)):
    item = db.query(Item)
    if not item:
        raise HTTPException(status_code=404,detail="Item Not Found")
    return item

@app.get("/items/{item_id}",response_model=ItemResponse)
async def get_byId(item_id:int,db:Session=Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404,detail="Item Not Found")
    return db_item




@app.put("/items/{item_id}",response_model = ItemResponse)
async def update_Item(item_id : int,item_data : dict ,db : Session = Depends(get_db)):
    db_items = db.query(Item).filter(Item.id == item_id).first()
    if db_items:
        for key,value in item_data.items():
            setattr(db_items,key,value)
        db.commit()
        return db_items
    else:
        raise HTTPException(status_code=404, detail="item not found")

@app.delete("/items/{item_id}",response_model=ItemResponse)
async def delete_item(item_id:int,db:Session = Depends(get_db)):
    db_items = db.query(Item).filter(Item.id == item_id).first()
    if db_items:
        db.delete(db_items)
        db.commit()
        return db_items
    else:
        raise HTTPException(status_code=404,detail="item not found")


if __name__ == "__main__": 
	import uvicorn

	uvicorn.run(app, host="127.0.0.1", port=8000)
