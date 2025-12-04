from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

fruits = ["apple", "banana", "cherry"]

class FruitDict(BaseModel):
    name: str

class FruitResponse(BaseModel):
    id: int
    name: str

@app.get("/fruits")
def list_fruits() -> dict[str, list[FruitResponse]]:
    """모든 과일 조회"""
    return {"fruits": [{"id": index, "name": fruit} for index, fruit in enumerate(fruits)]}

@app.get("/fruits/{fruit_id}")
def get_fruit(fruit_id: int) -> FruitResponse | dict[str, str]:
    """특정 과일 조회"""
    if 0 <= fruit_id < len(fruits):
        return FruitResponse(id=fruit_id, name=fruits[fruit_id])
    else:
        return {"error": "Fruit not found"}


@app.post("/fruits")
def add_fruit(fruit: FruitDict) -> FruitResponse:
    """과일 추가"""
    fruits.append(fruit.name)
    return FruitResponse(id=len(fruits) - 1, name=fruit.name)
