# 🖼️ Flask Image Processor

画像前処理（ヒストグラム表示・輪郭抽出など）を行う Flask アプリケーションです。  
HTML UI 経由で画像をアップロードし、処理済み画像を確認できます。

---

## 🚀 クイックスタート（Docker使用）

### ✅ 前提条件

- [Docker](https://docs.docker.com/get-docker/) がインストールされていること

---

### 1. レポジトリをクローン

```bash
git clone https://github.com/yourusername/flask-image-processor.git
cd flask-image-processor
```
### 2. Dockerイメージをビルド

```bash
docker build -t flask-processor .
```
※ 初回は数分かかります

### 3. アプリ起動

```bash
docker build -t flask-processor .
```

### 4. ブラウザでアクセス

http://localhost:5000 にアクセスすると、画像アップロードUIが表示されます。


## 📁 ディレクトリ構成
```
.
├── app/
│   ├── main.py         ← Flaskエントリーポイント
│   ├── processor.py    ← OpenCVによる画像処理
│   ├── templates/      ← index.html
│   └── static/         ← 処理後画像などの保存場所
├── requirements.txt    ← 必要なPythonライブラリ
├── Dockerfile          ← 実行環境定義
└── .dockerignore       ← ビルド除外設定

```