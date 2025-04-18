

# 🧱 Djangoにおける `models.py` の挙動とデータベース構築の流れ

Djangoでは、データベース操作をSQLではなく**Pythonコードで抽象化して記述する**ことができます。  
そのために使われるのが、`models.py` とマイグレーションシステムです。

---

## 🏗 各工程の役割と比喩イメージ

| ステップ | 実体 | 比喩 |
|----------|------|------|
| `models.py` のクラス定義 | モデルクラス（例：`Material`） | **建物の設計図**（何をどう作るか） |
| `makemigrations` 実行 | マイグレーションファイル生成（例：`0001_initial.py`） | **工事の実施計画書**（どのように施工するか） |
| `migrate` 実行 | SQLに変換され、Supabaseに送信 | **設計と計画に基づいて実際に建築する作業** |
| Supabase側 | PostgreSQLが動くクラウドDB | **土地の上に建物を建ててくれる施工業者（API経由）** |

---

## 🔄 処理フローまとめ（実行される内容）

1. **`models.py` にモデルクラスを記述**
    - Djangoアプリ内に `Material`, `UserProfile` などのモデルを書く
    - 各フィールドはテーブルのカラムに対応

2. **`python manage.py makemigrations`**
    - モデルの変更を検知し、マイグレーションファイル（Pythonコード）を作成
    - ファイル名は通常 `0001_initial.py` や `0002_auto_xxxx.py`

3. **`python manage.py migrate`**
    - マイグレーションファイルを元に**SQLコマンドを自動生成**
    - Supabase/PostgreSQLにAPI経由で送信
    - 対応するテーブルがSupabaseに作成される

---

## 🧩 これにより得られるメリット

- **SQLを書かずにDB設計・操作が可能**
- **DjangoアプリとDB構造が自動的に同期される**
- **SupabaseのGUIやREST APIとも連携しやすい**
- **チームや本番・開発環境間の再現性も高い**

---

## 📝 具体例（まとめ）

```bash
# 設計図を書く
models.py にモデルクラスを定義

# 設計から施工計画を生成
python manage.py makemigrations

# 施工計画をSupabaseに送り、建物を建てる
python manage.py migrate

# SupabaseがPostgreSQLを使ってテーブルを作成
→ GUI上に反映され、データの保存や取得が可能に
```

---

