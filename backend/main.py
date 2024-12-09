from fastapi import FastAPI, HTTPException
from typing import List, Dict
from pydantic import BaseModel

app = FastAPI()

# インメモリでのデータ保存
todos: Dict[int, dict] = {}
counter = 0

class Todo(BaseModel):
    title: str
    completed: bool = False

@app.get("/todos", response_model=List[Dict])
async def get_todos():
    return list(todos.values())

@app.post("/todos")
async def create_todo(todo: Todo):
    global counter
    counter += 1
    todo_dict = {"id": counter, "title": todo.title, "completed": todo.completed}
    todos[counter] = todo_dict
    return todo_dict

@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, completed: bool):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    todos[todo_id]["completed"] = completed
    return todos[todo_id]

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos[todo_id]
    return {"message": "Todo deleted"}