# プロジェクト構成ガイド

画像前処理（背景除去や輪郭抽出など）を、WebUIを通じて誰でも簡単に扱えることを目的としたコード。
Flask + OpenCV + Dockerを掛け合わせるという、学習としての側面が強い。
---

## 📁 ディレクトリ構成
```
project/
├── app/
│   ├── main.py            # Flaskアプリのエントリーポイント
│   ├── processor.py       # OpenCVを使った画像前処理ロジック
│   ├── templates/
│   │   └── index.html     # HTMLフォームUI（Flaskテンプレート）
│   └── static/            # 処理後の画像やCSS/JavaScriptを格納
├── Dockerfile             # Dockerビルド設定ファイル
├── requirements.txt       # 使用ライブラリ一覧（Flask, OpenCV等）
├── .dockerignore          # Dockerビルド時に除外するファイル
└── README.md              # プロジェクト説明ファイル（この文書）
```

## 🔧 各ファイル・フォルダの説明

| ファイル・フォルダ         | 説明                                                                 |
|----------------------------|----------------------------------------------------------------------|
| `app/main.py`              | Flaskアプリの起動スクリプト。ルーティングや画像処理呼び出しを担当。 |
| `app/processor.py`         | OpenCVによる画像処理ロジックを定義したモジュール。                 |
| `app/templates/index.html` | ユーザーが画像アップロードや処理パラメータを設定するUI。           |
| `app/static/`              | 処理結果画像やスタイル・スクリプトなどの静的ファイル格納場所。      |
| `Dockerfile`               | Dockerコンテナを構築するためのレシピ。                             |
| `requirements.txt`         | Pythonの依存ライブラリを列挙。Dockerビルド時に使用。                |
| `.dockerignore`            | 不要なファイルをDockerイメージから除外する設定。                   |
| `README.md`                | プロジェクトの概要、構成、使い方などを記載する文書。                 |

---

## 💡 補足

- Dockerを使っているため、ローカル環境にPythonやFlaskを直接インストールせずとも動作します。
- Flaskのテンプレート機能を用いて、HTMLとPythonの連携がスムーズに行えます。
- 静的ファイルやテンプレートはFlaskのディレクトリ構成に準拠しています。
