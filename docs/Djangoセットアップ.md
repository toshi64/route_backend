# Djangoプロジェクトのセットアップとデプロイ手順

## 概要
このドキュメントでは、Djangoプロジェクトの立ち上げからRenderへのデプロイまでの手順を説明します。

## 0. 使用するPythonとDjangoのバージョン確認（初期段階で必須）

開発前に、使用したい Django のバージョンが、現在の Python バージョンと互換性があるか確認しておきます。  
仮想環境は **対応する Python のバージョンで作成**するようにしましょう。

### 🔸 例：

- Django 5.0 以上 → Python 3.10〜3.12 が必要
- Django 4.2 → Python 3.8〜3.11

# 現在のPythonバージョン確認
python --version

# 必要に応じて pyenv などで切り替え
pyenv install 3.12.2
pyenv local 3.12.2


## 1. 仮想環境の作成
ローカルで仮想環境を作成し、必要なパッケージをインストールします。


## 2. Djangoのインストール
仮想環境内でDjangoをインストールします。

## 3. Djangoプロジェクトの立ち上げ
Djangoプロジェクトを作成します。

## 4. `.env` ファイルの作成
- `.env` ファイルを作成し、環境変数を設定します。
- `python-dotenv` を使用して環境変数を読み込む設定を行います。
- `settings.py` の `SECRET_KEY` を `.env` の値で置き換えます。

## 5. Adminが立ち上がるか確認
Djangoの管理サイトが正常に動作するか確認します。

## 6. アプリの作成
Djangoプロジェクト内で新しいアプリを作成し、`settings.py` の `INSTALLED_APPS` に追加します。

## 6.5 カスタムユーザーモデルの設定（初期段階で必須）【追記】

Djangoで独自のユーザーモデル（メールログインなど）を使用する場合は、**必ず最初の段階で定義**しておく必要があります。あとから変更することはできません。

1. 作成したアプリ（例：`accounts`）の中に `models.py` を作成し、以下を記述します：

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
```

2. `settings.py` に以下を追加します：

```python
AUTH_USER_MODEL = 'accounts.CustomUser'
```

3. モデルのマイグレーションを反映します：

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

> 🔸 注意：この設定は、**プロジェクト作成直後、最初のマイグレーション前に必ず行ってください。**
```

---

## 7. ルーティングの設定
- プロジェクトの `urls.py` でアプリのURLを指定します。
- アプリの `urls.py` でビュー関数を指定します。

## 8. ビュー関数の実装
`views.py` にテスト用の処理を実装します。今回は受け取ったデータをコンソールに出力します。

## 9. CORS設定
- `django-cors-headers` をインストールします。
- `settings.py` に以下を追加します：
  - `INSTALLED_APPS` に `corsheaders`
  - `MIDDLEWARE` に `corsheaders.middleware.CorsMiddleware`
  - `CORS_ALLOWED_ORIGINS` に許可するオリジンを設定します。

## 10. CSRF設定
- アプリの `views.py` で `csrf_exempt` をインポートします。
- ビュー関数に `@csrf_exempt` デコレーターを適用します。

## 11. Procfileの作成
プロジェクトのルートディレクトリに拡張子なしの `Procfile` を作成し、必要な内容を記述します。

## 12. gunicornのインストール
`gunicorn` をインストールします。

## 13. `settings.py` の更新
`ALLOWED_HOSTS` にRenderのドメインを追加します。

## 14. `requirements.txt` の作成
使用しているライブラリ（`python-dotenv`, `django-cors-headers`, `gunicorn`）を `requirements.txt` に記述します。

## 15. `.gitignore` の作成
ルートディレクトリに `.gitignore` を作成し、以下を追加します：
- `.env`
- `__pycache__/`
- `*.pyc`
- `db.sqlite3`

## 16. GitHubへプッシュ
プロジェクトをGitHubにプッシュします。

## 17. Renderへの接続
Renderにプロジェクトを接続し、デプロイを行います。
環境変数へのSECRET_KEYの登録を忘れずに。
