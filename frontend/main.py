import flet as ft
import httpx
import asyncio

class TodoApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Todo App"  # ページのタイトルを設定
        self.api_base_url = "http://localhost:8000"  # バックエンドAPIのベースURLを設定
        
        # UIコンポーネントの初期化
        self.new_task = ft.TextField(
            hint_text="新しいタスクを入力",  # ユーザーに入力を促すヒントテキスト
            expand=True,  # テキストフィールドを利用可能なスペースに拡張
            on_submit=self.add_clicked  # Enterキー押下時のイベントハンドラ
        )
        self.tasks = ft.Column()  # タスク一覧を表示するカラム
        
        # レイアウトの設定
        self.page.add(
            ft.Row([
                self.new_task,  # 新しいタスクを入力するテキストフィールド
                ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked)  # 追加ボタン
            ]),
            self.tasks  # タスク一覧の表示エリア
        )
    
    async def add_clicked(self, e):
        if not self.new_task.value:
            return  # 入力が空の場合は何もしない
        
        # APIを呼び出して新しいTodoを作成
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base_url}/todos",
                json={"title": self.new_task.value}
            )
            if response.status_code == 200:
                todo = response.json()
                await self.add_task_to_view(todo)  # ビューにタスクを追加
                self.new_task.value = ""  # テキストフィールドをクリア
                await self.new_task.focus_async()  # テキストフィールドにフォーカスを戻す
                await self.page.update_async()  # ページを更新
    
    async def add_task_to_view(self, todo):
        # タスクの削除ボタンがクリックされた時の処理
        async def remove_clicked(e):
            async with httpx.AsyncClient() as client:
                await client.delete(f"{self.api_base_url}/todos/{todo['id']}")
                await self.load_todos()  # タスク一覧を再読み込み
    
        # チェックボックスの状態が変更された時の処理
        async def checkbox_changed(e):
            async with httpx.AsyncClient() as client:
                await client.put(
                    f"{self.api_base_url}/todos/{todo['id']}", 
                    params={"completed": e.control.value}
                )
    
        # タスクを表示するためのRowレイアウト
        task_row = ft.Row(
            controls=[
                ft.Checkbox(
                    value=todo["completed"],  # タスクの完了状態
                    label=todo["title"],  # タスクのタイトル
                    on_change=checkbox_changed  # 状態変更時のイベントハンドラ
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,  # 削除アイコン
                    on_click=remove_clicked  # クリック時のイベントハンドラ
                )
            ]
        )
        self.tasks.controls.append(task_row)  # タスク一覧に追加
    
    async def load_todos(self):
        # バックエンドからタスク一覧を取得
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_base_url}/todos")
            if response.status_code == 200:
                todos = response.json()
                self.tasks.controls.clear()  # 既存のタスク表示をクリア
                for todo in todos:
                    await self.add_task_to_view(todo)  # 各タスクをビューに追加
                await self.page.update_async()  # ページを更新

# アプリケーションのエントリーポイント
async def main(page: ft.Page):
    app = TodoApp(page)  # TodoAppのインスタンスを作成
    await app.load_todos()  # 初期タスク一覧を読み込む

ft.app(target=main, view=ft.AppView.WEB_BROWSER)  # アプリをWebブラウザで起動