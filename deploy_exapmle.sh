#!/bin/bash
set -e

# --- 設定項目（記入が必要）---
PROJECT_ID="YOUR_PROJECT_ID"  # GCPのプロジェクトIDを記入
SERVICE_NAME="wifi-qrcode-service"
REGION="asia-northeast1"
IMAGE_NAME="wifi-qrcode-app"
TAG="latest"
DIFY_API_KEY="your_dify_api_key"  # DifyのAPIキーを設定
API_SERVER="https://yourendpointurl/v1"  # APIサーバーURLを設定
DIFY_BASE_URL="https://yourdifybaseurl" # DifyのベースURLを設定

# Docker イメージのビルド
echo "🐳 Docker イメージをビルドしています..."
docker build --platform=linux/amd64 -t gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG} .

# Docker イメージのプッシュ
echo "📤 Docker イメージを GCR にプッシュしています..."
docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

# Cloud Run へのデプロイ（環境変数 DIFY_API_KEY, API_SERVER を設定）
echo "🚀 Cloud Run へデプロイしています..."
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG} \
  --platform managed \
  --region ${REGION} \
  --set-env-vars DIFY_API_KEY=${DIFY_API_KEY},API_SERVER=${API_SERVER},DIFY_BASE_URL=${DIFY_BASE_URL} \
  --allow-unauthenticated

echo "✅ デプロイ完了！Cloud Run のサービスが公開されました！"