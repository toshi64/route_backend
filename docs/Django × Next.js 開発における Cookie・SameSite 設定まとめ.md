
# Django × Next.js 開発における Cookie・SameSite 設定まとめ

## 🍪 SameSite属性とは？
Cookieの送信可否を制御する仕組み。セキュリティ向上のため、近年はデフォルトが厳しくなっている。

| 属性値 | 意味 | JavaScriptからのfetchで送られる？ |
|--------|------|------------------------------------|
| Strict | 完全に同一オリジンのみ許可 | ❌ 送られない |
| Lax    | トップレベルのGETや同一オリジンのみ許可 | 🔶 一部OK／POSTやJSはNG |
| None   | 完全に許可（ただし Secure=True が必須） | ✅ 送られる |

---

## ✅ ローカル開発環境での推奨設定

### 🛠 想定URL
- フロントエンド：`http://localhost:3000`
- バックエンド　：`http://localhost:8000`

### 🔧 Djangoのsettings.py

```python
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
```

### 🔧 Next.js（fetch）

```js
fetch("http://localhost:8000/api/accounts/me/", {
  method: "GET",
  credentials: "include"
})
```

### 💡 注意点
- `127.0.0.1` と `localhost` は**異なるドメイン扱い**
- 両者で統一しないと Cookie が送られない！

---

## ✅ 本番環境（別ドメイン間）での推奨設定

### 🛠 想定URL
- フロントエンド：`https://my-app.vercel.app`
- バックエンド　：`https://api.my-app.onrender.com`

### 🔧 Djangoのsettings.py

```python
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True
```

### 🔧 CORS設定（settings.py）

```python
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://my-app.vercel.app",
]
```

### 🔧 Next.js（fetch）

```js
fetch("https://api.my-app.onrender.com/api/accounts/me/", {
  method: "GET",
  credentials: "include"
})
```

### 💡 注意点
- `SameSite=None` を使うときは必ず `Secure=True`
- フロント・バックとも **HTTPS** でなければ Cookie は保存も送信もされない！

---

## 🔁 よくある落とし穴と対処法

| 現象 | 原因 | 対処法 |
|------|------|--------|
| Cookieが保存されない | `SameSite=None` + `Secure=False` | Secure=Trueにする or SameSite=Laxに戻す |
| Cookieが送られない | ドメイン不一致 (`localhost` vs `127.0.0.1`) | URLを統一する |
| Django側で `AnonymousUser` になる | Cookieが送られてない | fetchに `credentials: 'include'` を付ける、SameSite/ドメイン確認 |

---

## 📌 開発と本番の切り替えを `.env` で管理する例

```python
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
```

```
# .env.development
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_SECURE=False

# .env.production
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_SECURE=True
```

---

## ✅ まとめ

- ローカルでは `Lax` + `Secure=False` でOK
- 本番では `None` + `Secure=True` が必須
- Cookie送信には fetch/axios に `credentials: 'include'` を忘れずに！
- ドメイン（`localhost` vs `127.0.0.1`）を揃えよう

---

---
