# Wi-Fi QR Generator

このアプリケーションは、Wi‑Fi 情報を含むオブジェクト（例：ルーターなど）の写真を撮影し、外部の Dify ワークフロー API を利用して Wi‑Fi 接続用の QR コードを生成する Streamlit ベースの Web アプリです。生成された QR コードは表示・ダウンロード、または LINE での共有が可能です。

---

## 目次

- [特徴](#特徴)
- [必要な環境](#必要な環境)
- [インストール](#インストール)
- [環境変数の設定](#環境変数の設定)
- [ローカルでの実行](#ローカルでの実行)
- [Docker コンテナのビルドとデプロイ](#docker-コンテナのビルドとデプロイ)
- [Cloud Run へのデプロイ手順](#cloud-run-へのデプロイ手順)
- [注意点](#注意点)

---

## 特徴

- **カメラ起動機能**  
  ユーザーはブラウザ上でカメラを起動し、Wi‑Fi 情報が含まれるオブジェクトの写真を撮影できます。

- **QR コード生成**  
  撮影した画像を外部の Dify ワークフロー API に送信し、Wi‑Fi 接続用の QR コードを生成します。

- **QR コードの表示・保存・共有**  
  生成された QR コードを画面に表示し、ダウンロードや LINE での共有が可能です。

- **Cloud Run でのデプロイ対応**  
  Docker コンテナとしてパッケージ化され、Google Cloud Run などのクラウド環境へのデプロイが容易です。

---

## 必要な環境

- **Python 3.10** 以上
- **Docker**
- **Google Cloud SDK** (gcloud コマンド)
- Google Cloud Platform アカウントおよび Cloud Run 利用の設定

---

## インストール

### リポジトリのクローン

```bash
git clone https://github.com/yourusername/yourrepository.git
cd yourrepository
```
Python ライブラリのインストール (ローカル実行の場合)
```bash
pip install -r requirements.txt
```
## 環境変数の設定
このアプリケーションでは、外部 API（Dify ワークフロー API）を利用する際の認証に DIFY_API_KEY を使用します。

ローカル実行の場合
実行前に、環境変数を設定してください。例：
```bash
export DIFY_API_KEY="your_dify_api_key"
```
## Cloud Run での設定
deploy.sh スクリプト内で --set-env-vars DIFY_API_KEY=${DIFY_API_KEY} オプションを使用して自動的に設定します。
※スクリプト内の変数 DIFY_API_KEY を実際の認証キーに置き換えてください。

## ローカルでの実行
以下のコマンドで Streamlit アプリを起動できます。
```bash
streamlit run app.py
```
ブラウザが自動的に起動し、アプリの UI が表示されます。

Docker コンテナのビルドとデプロイ
Docker イメージのビルド
Dockerfile を使用して、以下のコマンドでイメージをビルドします。
PROJECT_ID は Google Cloud プロジェクトの ID に置き換えてください。

```bash
docker build -t gcr.io/PROJECT_ID/wifi-qrcode-app:latest .
```
Docker イメージのプッシュ
ビルドしたイメージを Google Container Registry (GCR) にプッシュします。

```bash
docker push gcr.io/PROJECT_ID/wifi-qrcode-app:latest
```
Cloud Run へのデプロイ手順
デプロイは、同梱の deploy.sh スクリプトを利用して自動化できます。
スクリプト内の各変数（PROJECT_ID、SERVICE_NAME、REGION、IMAGE_NAME、TAG、DIFY_API_KEY）を自身の環境に合わせて設定してください。

## 手順
deploy.sh の実行権限を付与
```bash
chmod +x deploy.sh
```
デプロイの実行
```bash
./deploy.sh
```
このスクリプトは以下の処理を行います：

Docker イメージのビルド
Docker イメージの GCR へのプッシュ
gcloud コマンドを利用した Cloud Run へのデプロイ
※デプロイ時に環境変数 DIFY_API_KEY も設定され、認証なしでアクセスできる状態になります（必要に応じてセキュリティ設定を変更してください）。
## 注意点

- DIFY_API_KEY
    - Dify ワークフロー API を利用するための認証キーです。必ず正しい値を設定してください。
- セキュリティ
    Cloud Run では --allow-unauthenticated オプションにより認証なしでアクセス可能となっています。運用環境に応じてアクセス制御の設定を検討してください。
- API エンドポイント
    - app.py 内の API エンドポイント URL (http://elecnecta.jp/v1/workflows/run) はサンプルです。実際の API の URL に合わせて修正してください。

