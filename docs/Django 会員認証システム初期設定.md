
# 🛠 Django 会員認証システム初期設定

個人開発・API設計に対応した、セッションベースの認証機能（Signup / Login / Logout）の最小構成を実装するための手順です。Next.jsなどとの接続も視野に入れた形で構成されています。

---

## ✅ ① `settings.py` で確認する設定内容

### 🔸 INSTALLED_APPS

以下が含まれていることを確認：

```python
INSTALLED_APPS = [
    ...,
    'accounts',              # ← ユーザー管理用アプリ（自作）
    'django.contrib.auth',   # 認証システムの本体
    'django.contrib.contenttypes',  # モデル管理の内部基盤
    'django.contrib.sessions',      # セッション管理
    'django.contrib.messages',      # ログインメッセージなど
]
```

### 🔸 MIDDLEWARE

```python
MIDDLEWARE = [
    ...,
    'django.contrib.sessions.middleware.SessionMiddleware',  # セッション識別
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # request.user の有効化
]
```

### 🔸 カスタムユーザーモデルを使用する宣言

```python
AUTH_USER_MODEL = 'accounts.CustomUser'
```

---

## ✅ ② カスタムユーザーモデルの定義（`accounts/models.py`）

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

マイグレーションの反映：

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

---

## ✅ ③ ビュー関数とルーティングの作成

### 🔹 `accounts/views.py`

```python
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            username = data.get('username', '')

            user = CustomUser.objects.create_user(email=email, password=password, username=username)
            login(request, user)
            return JsonResponse({'message': 'User created'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'POST only'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'POST only'}, status=405)

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logged out'}, status=200)
    return JsonResponse({'error': 'POST only'}, status=405)
```

---

### 🔹 `accounts/urls.py`

```python
from django.urls import path
from .views import signup_view, login_view, logout_view

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
```

---

### 🔹 プロジェクト側の `urls.py`

```python
from django.urls import path, include

urlpatterns = [
    ...,
    path('', include('accounts.urls')),
]
```

---

## ✅ ④ Thunder Client でのテスト手順

### 🔸 基本的なリクエスト設定（POST）

- URL：`http://localhost:8000/signup/`（または `/login/`）
- Method：`POST`
- Headers：`Content-Type: application/json`
- Body（raw JSON）例：

```json
{
  "email": "test@example.com",
  "password": "test1234",
  "username": "tester"
}
```

---

### 🔸 クッキーの確認方法

1. リクエスト送信後、Thunder Client の「Cookies」タブを確認  
2. `sessionid` と `csrftoken` が表示されていればログイン成功  
3. `/logout/` にPOST後、`sessionid` が削除されていればログアウト成功

---

## ✅ 💡補足：ログイン状態の確認用エンドポイント（任意）

```python
from django.http import JsonResponse

def me_view(request):
    if request.user.is_authenticated:
        return JsonResponse({'email': request.user.email})
    else:
        return JsonResponse({'error': 'Not logged in'}, status=401)
```

---
