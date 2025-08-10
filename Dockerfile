# ベースイメージ（Python3.9以上を推奨）
FROM python:3.13-slim

# 作業ディレクトリを作成
WORKDIR /app

# OpenCVに必要なシステムライブラリをインストール
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && apt-get clean

# 必要ファイルをコピー
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをすべてコピー
COPY src ./src

WORKDIR /app/src

# Flaskアプリ起動
CMD ["python", "main.py"]
