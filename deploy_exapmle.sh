#!/bin/bash
set -e
# --- 設定項目 ---
PROJECT_ID="YOUR_PROJECT_ID"
SERVICE_NAME="vtq-qr-code-reader"
REGION="asia-northeast1"
IMAGE_NAME="vtq-qr-code-reader"
TAG="latest"
DIFY_API_KEY="your_dify_api_key"
# Docker イメージのビルド
echo "Docker イメージをビルドしています..."
docker build --platform=linux/amd64 -t gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG} .
# Docker イメージのプッシュ
echo "Docker イメージをプッシュしています..."
docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}
# Cloud Run へのデプロイ
echo "Cloud Run へデプロイしています..."
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG} \
  --platform managed \
  --region ${REGION} \
  --set-env-vars DIFY_API_KEY=${DIFY_API_KEY} \
  --allow-unauthenticated
echo "デプロイ完了！"
