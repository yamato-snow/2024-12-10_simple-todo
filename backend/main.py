from fastapi import FastAPI, HTTPException
from typing import List, Dict
from pydantic import BaseModel

# FastAPIのインスタンスを作成
# これがAPIアプリケーションの本体となります
app = FastAPI()

# インメモリ（プログラムのメモリ上）でデータを保存するための変数
# 実際のアプリではデータベースを使用しますが、簡単のためメモリ上に保存します
todos: Dict[int, dict] = {}  # todoリストを保存する辞書
counter = 0  # TodoのIDを管理するカウンター

# TodoのデータモデルをPydanticを使って定義
# これにより、データのバリデーション（検証）が自動的に行われます
class Todo(BaseModel):
    title: str  # タイトルは文字列型で必須
    completed: bool = False  # 完了フラグはブール型で、デフォルトはFalse

# GETメソッド: すべてのTodoを取得するエンドポイント
# response_modelで戻り値の型を指定できます
@app.get("/todos", response_model=List[Dict])
async def get_todos():
    # 辞書の値（Todo項目）のリストを返します
    return list(todos.values())

# POSTメソッド: 新しいTodoを作成するエンドポイント
@app.post("/todos")
async def create_todo(todo: Todo):
    global counter  # グローバル変数を使用することを宣言
    counter += 1  # IDをインクリメント
    # 新しいTodoを辞書形式で作成
    todo_dict = {"id": counter, "title": todo.title, "completed": todo.completed}
    todos[counter] = todo_dict  # 作成したTodoを保存
    return todo_dict  # 作成したTodoを返す

# PUTメソッド: 既存のTodoを更新するエンドポイント
@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, completed: bool):
    # 指定されたIDのTodoが存在しない場合は404エラー
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    # 完了状態を更新
    todos[todo_id]["completed"] = completed
    return todos[todo_id]

# DELETEメソッド: Todoを削除するエンドポイント
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    # 指定されたIDのTodoが存在しない場合は404エラー
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    # Todoを削除
    del todos[todo_id]
    return {"message": "Todo deleted"}