import flet as ft
import httpx
import asyncio

class TodoApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Todo App"
        self.api_base_url = "http://localhost:8000"
        
        # UI components
        self.new_task = ft.TextField(
            hint_text="新しいタスクを入力",
            expand=True,
            on_submit=self.add_clicked
        )
        self.tasks = ft.Column()
        
        # レイアウト
        self.page.add(
            ft.Row([
                self.new_task,
                ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked)
            ]),
            self.tasks
        )
    
    async def add_clicked(self, e):
        if not self.new_task.value:
            return
        
        # APIを呼び出してTodoを作成
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base_url}/todos",
                json={"title": self.new_task.value}
            )
            if response.status_code == 200:
                todo = response.json()
                await self.add_task_to_view(todo)
                self.new_task.value = ""
                await self.new_task.focus_async()
                await self.page.update_async()

    async def add_task_to_view(self, todo):
        async def remove_clicked(e):
            async with httpx.AsyncClient() as client:
                await client.delete(f"{self.api_base_url}/todos/{todo['id']}")
                await self.load_todos()

        async def checkbox_changed(e):
            async with httpx.AsyncClient() as client:
                await client.put(
                    f"{self.api_base_url}/todos/{todo['id']}", 
                    params={"completed": e.control.value}
                )

        task_row = ft.Row(
            controls=[
                ft.Checkbox(
                    value=todo["completed"],
                    label=todo["title"],
                    on_change=checkbox_changed
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,
                    on_click=remove_clicked
                )
            ]
        )
        self.tasks.controls.append(task_row)

    async def load_todos(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_base_url}/todos")
            if response.status_code == 200:
                todos = response.json()
                self.tasks.controls.clear()
                for todo in todos:
                    await self.add_task_to_view(todo)
                await self.page.update_async()

async def main(page: ft.Page):
    app = TodoApp(page)
    await app.load_todos()

ft.app(target=main, view=ft.AppView.WEB_BROWSER)