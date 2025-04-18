
# 📘 Supabase × Django × Render データベース連携セットアップ手順（完全版）

---

## 🔧 1. Supabase プロジェクト作成

- Supabaseにログインし、プロジェクトを作成
- プロジェクト名・DBパスワードを設定
- リージョンは Tokyo（推奨）

---

## 🔑 2. Supabase の接続情報を取得

Supabase ダッシュボード > `Database > Connection info` で以下を確認：

| 項目        | 値（例）                          |
|-------------|-----------------------------------|
| DB名        | `postgres`（固定）               |
| ユーザー名  | `postgres`（通常固定）           |
| パスワード  | プロジェクト作成時に設定したもの |
| ホスト名    | 例：`db.abc123xyz.supabase.co`   |
| ポート      | `5432`                            |

---

## 📦 3. 必要なライブラリをインストール

```bash
pip install psycopg2-binary python-dotenv supabase
```

---

## 📁 4. `.env`ファイルを作成（ローカル開発用）

```env
# データベース接続用
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=ここにDBパスワード
SUPABASE_DB_HOST=db.abc123xyz.supabase.co
SUPABASE_DB_PORT=5432

# Supabase API用（教材保存などに使う）
SUPABASE_URL=https://abc123xyz.supabase.co
SUPABASE_KEY=ここにサービスロールキー
```

> `.env` は `.gitignore` に追加すること！

---

## 🔐 5. Supabase APIキーとURLの取得

Supabase ダッシュボード > `Settings > API` で確認：

| 項目            | 説明                                      |
|-----------------|-------------------------------------------|
| `Project URL`   | → `.env` の `SUPABASE_URL` に設定         |
| `service_role`  | → `.env` の `SUPABASE_KEY` に設定（重要） |

---

## ⚙️ 6. `settings.py` に環境変数を読み込む設定を追加

```python
import os
from dotenv import load_dotenv
load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('SUPABASE_DB_NAME'),
        'USER': os.getenv('SUPABASE_DB_USER'),
        'PASSWORD': os.getenv('SUPABASE_DB_PASSWORD'),
        'HOST': os.getenv('SUPABASE_DB_HOST'),
        'PORT': os.getenv('SUPABASE_DB_PORT'),
    }
}

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
```

---

## 🛠 7. モデル定義（例）

```python
class Material(models.Model):
    user_id = models.IntegerField()
    timestamp = models.DateTimeField()
    user_prompt = models.TextField()
    text = models.TextField()
    title = models.CharField(max_length=255)
    title_ja = models.CharField(max_length=255)
    summary = models.TextField()
    summary_ja = models.TextField()
    raw_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 🚀 8. マイグレーション実行（Supabaseに反映）

```bash
python manage.py makemigrations
python manage.py migrate
```

→ Supabase「Table Editor」でテーブルを確認！

---

## 🧪 9. テストスクリプトで保存を試す

```python
# run_test_insert.py

import os
import django
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_backend.settings")
django.setup()

from material_generator.models import Material

Material.objects.create(
    user_id=999,
    timestamp=datetime.fromisoformat("2025-04-15T08:08:46+00:00"),
    user_prompt="テストプロンプトです。",
    text="This is a test article.",
    title="Test Title",
    title_ja="テストタイトル",
    summary="This is a summary.",
    summary_ja="これは要約です。",
    raw_data={"Q1": "ビジネス", "Q2": "起業家になりたい"}
)

print("✅ テストデータをSupabaseに保存しました！")
```

---

## ☁️ 10. Render に環境変数を登録する

### 手順：

1. [render.com](https://render.com) にログイン
2. 該当サービス（例：Djangoアプリ）を選択
3. 「**Environment > Environment Variables**」を開く
4. 以下のキーと `.env` と同じ値を登録：

| Key                     | 説明                               |
|-------------------------|------------------------------------|
| `SUPABASE_DB_NAME`      | 通常 `postgres`                    |
| `SUPABASE_DB_USER`      | 通常 `postgres`                    |
| `SUPABASE_DB_PASSWORD`  | DB接続用パスワード                 |
| `SUPABASE_DB_HOST`      | 例：`db.abc123xyz.supabase.co`    |
| `SUPABASE_DB_PORT`      | 通常 `5432`                        |
| `SUPABASE_URL`          | SupabaseのプロジェクトURL         |
| `SUPABASE_KEY`          | Supabaseのサービスロールキー（秘密） |


---

## 🧩 11. 接続方式の違いに注意！（Direct と Pooler）

Render で接続エラーが発生した原因は、**Supabaseの接続方式による違い**にありました。

### 🔄 問題の本質：
Supabaseの接続には大きく分けて2種類の方式があります：

| 接続方式             | ホスト名例                                           | ポート | USER名の例                     |
|----------------------|------------------------------------------------------|--------|-------------------------------|
| **Direct Connection**| `db.abc123xyz.supabase.co`                           | 5432   | `postgres`                    |
| **Transaction Pooler**| `aws-0-ap-northeast-1.pooler.supabase.com` など     | 6543   | `postgres.abc123xyz` の形式   |

### 😱 よくある落とし穴：

- `DB_HOST` と `DB_PORT` は変えたのに、**`DB_USER` を変えていなかった**ことでエラーに。
- Transaction Pooler を使う場合、**ユーザー名が `postgres.プロジェクトID` という形式**である必要があります。

### ✅ 解決策：

`.env`やRender環境変数において、**接続方式に応じて3つすべての値**を確認・一致させてください：

```env
SUPABASE_DB_HOST=aws-0-ap-northeast-1.pooler.supabase.com
SUPABASE_DB_PORT=6543
SUPABASE_DB_USER=postgres.abc123xyz   ← Project IDが含まれている！
```

> Supabase ダッシュボード「Connect > Connection string」からコピペで確認できます。

---

### 💡補足：
- **ローカルではDirectでOKでも、本番(Render)ではPooler推奨**のケースが多いです。
- Supabaseの無料プランでは、DirectはIPv6のみ・PoolerはIPv4対応という違いも。

---
