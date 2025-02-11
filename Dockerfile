# Python の軽量スリムイメージを利用
FROM python:3.10-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なライブラリをインストール
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# アプリケーションコードのコピー
COPY app.py .

# Cloud Run 用にポート 8080 を公開
EXPOSE 8080

# Streamlit 用の環境変数設定（ヘッドレスモード、CORS 無効化）
ENV STREAMLIT_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false

# コンテナ起動時に Streamlit アプリを起動
CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0
