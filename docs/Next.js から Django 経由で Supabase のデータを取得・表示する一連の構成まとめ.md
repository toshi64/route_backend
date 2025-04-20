
## ✅ Next.js から Django 経由で Supabase のデータを取得・表示する一連の構成まとめ

### 1. **Next.js プロジェクトを立ち上げる**

- `npx create-next-app@latest` などでプロジェクトを作成
- ディレクトリ構成は App Router（`src/app/`）で進める
- Tailwind CSS なども初期設定しておくとUI調整が楽

---

### 2. **Next.js を Vercel にデプロイする**

- GitHubにプッシュ → Vercel と連携
- `.env` の環境変数（例：`NEXT_PUBLIC_API_BASE_URL`）をVercelの設定画面から登録
- APIのURLには **Django（Renderにデプロイ済み）側のURLを指定**

---

### 3. **Django の `views.py` に API エンドポイントを設定**

- 例：`/api/material/<id>/` のようなエンドポイントを作成
- `supabase-python` SDK を使って、Supabase のテーブル（例：`material_generator_material`）からデータを取得
- 取得したデータを `JsonResponse` で返す構成

```python
response = supabase.table("material_generator_material").select("*").eq("id", material_id).single().execute()
```

---

### 4. **Django 側のテーブル構成に合わせてデータ取得処理を実装**

- 取得するフィールドは：`title`, `title_ja`, `summary`, `summary_ja`, `text` など
- Supabaseに保存された教材情報をもとに、クライアントに必要なデータだけ返すよう整形
- Supabaseのテーブル名はマイグレーション時に自動でつけられているので、これと一致するように注意。

---

### 5. **Next.js 側で環境変数に Django のURLを設定**

`.env.local` に以下を記述：

```env
NEXT_PUBLIC_API_BASE_URL=https://your-django-backend.onrender.com/api
```

これを `fetch()` などで使用：

```js
fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/material/${id}/`)
```

---

### 6. **Next.js の `page.jsx` に教材表示用のコードを実装**

- ユーザーが教材IDを選べるようにプルダウン（`<select>`）を設置
- 選択されたIDに応じて教材情報を取得 → 画面にレンダリング
- Tailwindでレイアウトを調整し、タイトル・要約・本文を表示

---

これで「**Next.js → Django API → Supabase → JSON → Next.jsに表示**」のデータ取得フローが完成します！
