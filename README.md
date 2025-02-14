# VTQ（Vision to QR） Wi-Fi Reader

## 概要
VTQ Wi-Fi Reader は、Wi-Fi 情報を含むオブジェクト（例：ポスターなど）の写真を撮影し、外部の Dify ワークフロー API を利用して Wi-Fi 接続用の QR コードを生成する Streamlit ベースの Web アプリです。生成された QR コードは表示・ダウンロードが可能です。

## 目次
- [特徴](#特徴)
- [アプリの設計](#アプリの設計)
- [必要な環境](#必要な環境)
- [インストール](#インストール)
- [環境変数の設定](#環境変数の設定)
- [ローカルでの実行](#ローカルでの実行)
- [Docker コンテナのビルドとデプロイ](#docker-コンテナのビルドとデプロイ)
- [Cloud Run へのデプロイ手順](#cloud-run-へのデプロイ手順)
- [注意点](#注意点)

## 特徴
- **カメラ起動機能**  
  ユーザーはブラウザ上でカメラを起動し、Wi-Fi 情報が含まれるオブジェクトの写真を撮影できます。
- **QR コード生成**  
  撮影した画像を外部の Dify ワークフロー API に送信し、Wi-Fi 接続用の QR コードを生成します。
- **QR コードの表示・保存・共有**  
  生成された QR コードを画面に表示し、ダウンロードや LINE での共有が可能です。
- **Cloud Run でのデプロイ対応**  
  Docker コンテナとしてパッケージ化され、Google Cloud Run などのクラウド環境へのデプロイが容易です。

## アプリの設計
このアプリは Streamlit を使用して開発されており、以下の構成で動作します。

1. **画像のアップロード・撮影**
   - ユーザーはカメラで撮影、または画像をアップロード可能。
2. **Dify API を用いた処理**
   - 画像は Dify ワークフロー API に送信され、Wi-Fi 情報を解析。
3. **QR コードの生成・表示**
   - 解析結果から Wi-Fi 接続用 QR コードを作成し、表示。
4. **共有機能**
   - QR コードのダウンロード、LINE での共有が可能。

## 必要な環境
- **Python 3.10** 以上
- **Docker**
- **Google Cloud SDK** (gcloud コマンド)
- Google Cloud Platform アカウントおよび Cloud Run 利用の設定

## インストール
### リポジトリのクローン
```bash
git clone https://github.com/yourusername/yourrepository.git
cd yourrepository
```
### Python ライブラリのインストール (ローカル実行の場合)
```bash
pip install -r requirements.txt
```
### 環境変数の設定
DIFY_API_KEY などの環境変数を設定する必要があります。<br>
ローカル実行の場合:
```bash
export DIFY_API_KEY="your_dify_api_key"
```
同様に、他の変数も設定してください。<br>
Cloud Run デプロイ時には deploy.sh スクリプト内で --set-env-vars オプションを使用して環境変数を設定します。
### ローカルでの実行
以下のコマンドで Streamlit アプリを起動できます。

```bash
streamlit run app.py
```
ブラウザが自動的に起動し、アプリの UI が表示されます。

### Docker コンテナのビルドとデプロイ
Docker イメージのビルド
以下のコマンドで Docker イメージをビルドします。
```bash
docker build -t gcr.io/PROJECT_ID/wifi-qrcode-app:latest .
```
Docker イメージのプッシュ
```bash
docker push gcr.io/PROJECT_ID/wifi-qrcode-app:latest
```
### Cloud Run へのデプロイ
デプロイは deploy.sh スクリプトを使用して自動実行します。
deploy.sh の実行権限を付与:
```bash
chmod +x deploy.sh
```
デプロイの実行:
```bash
./deploy.sh
```
このスクリプトは以下の処理を行います。
- Docker イメージのビルド
- Cloud Run へのデプロイ
## 注意点
### Difyワークフローのファイルについて
- 「VTQ Wi‑Fi Reader v2.yml」のファイルにDifでインポートできるワークフローDSLをアップロードしてありますので、お使いください。
   - deploy.sh にある DIFY_API_KEY、API_SERVER、DIFY_BASE_URLをご自身のDifyの環境に書き換えてください。