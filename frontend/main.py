import flet as ft
import httpx
import asyncio

class TodoApp:
    def __init__(self, page: ft.Page):
        """
        Todoアプリケーションのメインクラス
        Args:
            page: Fletのページオブジェクト
        """
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
            # 入力フィールドと追加ボタンを横に並べる
            ft.Row([
                self.new_task,  # 新しいタスクを入力するテキストフィールド
                ft.FloatingActionButton(  # 追加ボタン
                    icon=ft.icons.ADD,  # アイコンを設定
                    on_click=self.add_clicked  # クリック時のイベントハンドラ
                )
            ]),
            self.tasks  # タスク一覧の表示エリア
        )
    
    async def add_clicked(self, e):
        """
        タスク追加ボタンがクリックされたときの処理
        Args:
            e: イベントオブジェクト
        """
        if not self.new_task.value:
            return  # 入力が空の場合は何もしない
        
        # HTTPクライアントを使ってAPIを呼び出す
        async with httpx.AsyncClient() as client:
            # POSTリクエストでTodoを作成
            response = await client.post(
                f"{self.api_base_url}/todos",
                json={"title": self.new_task.value}
            )
            if response.status_code == 200:
                todo = response.json()
                # 画面にタスクを追加
                await self.add_task_to_view(todo)
                # 入力フィールドをクリアしてフォーカス
                self.new_task.value = ""
                await self.new_task.focus_async()
                # 画面を更新
                await self.page.update_async()

    async def add_task_to_view(self, todo):
        """
        タスクをUIに追加する処理
        Args:
            todo: APIから返されたTodoデータ
        """
        # 削除ボタンがクリックされたときの処理
        async def remove_clicked(e):
            async with httpx.AsyncClient() as client:
                # DELETEリクエストでTodoを削除
                await client.delete(f"{self.api_base_url}/todos/{todo['id']}")
                # タスクリストを再読み込み
                await self.load_todos()

        # チェックボックスの状態が変更されたときの処理
        async def checkbox_changed(e):
            async with httpx.AsyncClient() as client:
                # PUTリクエストでTodoの状態を更新
                await client.put(
                    f"{self.api_base_url}/todos/{todo['id']}", 
                    params={"completed": e.control.value}
                )

        # タスク1つ分のUI要素を作成
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
        # タスクリストに追加
        self.tasks.controls.append(task_row)

    async def load_todos(self):
        """
        すべてのTodoをAPIから読み込む処理
        """
        async with httpx.AsyncClient() as client:
            # GETリクエストでTodo一覧を取得
            response = await client.get(f"{self.api_base_url}/todos")
            if response.status_code == 200:
                todos = response.json()
                # タスクリストをクリア
                self.tasks.controls.clear()
                # 取得したTodoを1つずつUIに追加
                for todo in todos:
                    await self.add_task_to_view(todo)
                # 画面を更新
                await self.page.update_async()

# アプリケーションのメインエントリーポイント
async def main(page: ft.Page):
    app = TodoApp(page)  # アプリケーションのインスタンスを作成
    await app.load_todos()  # 初期データを読み込む

# アプリケーションを起動
# view=ft.AppView.WEB_BROWSERでブラウザで開く
ft.app(target=main, view=ft.AppView.WEB_BROWSER)