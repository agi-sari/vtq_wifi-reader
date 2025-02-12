import streamlit as st
import requests
import os
import uuid
from PIL import Image
from io import BytesIO

# **Dify API 設定**
DIFY_BASE_URL = "https://elecnecta.jp"
DIFY_API_KEY = os.getenv("DIFY_API_KEY")
HEADERS = {"Authorization": f"Bearer {DIFY_API_KEY}"}

st.title("カメラ入力 & 画像処理アプリ")

# **カメラで撮影または画像をアップロード**
uploaded_file = st.camera_input("カメラから画像を撮影") or st.file_uploader("画像を選択", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file:
    try:
        # **1. 画像を Dify にアップロード**
        st.write("📤 画像をアップロード中...")

        # MIME タイプの取得（適切でない場合はデフォルト設定）
        mime_type = uploaded_file.type if uploaded_file.type else "image/png"

        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), mime_type)
        }
        data = {"user": str(uuid.uuid4())}

        response = requests.post(
            f"{DIFY_BASE_URL}/v1/files/upload",
            headers=HEADERS,
            files=files,
            data=data,
            timeout=60
        )

        if response.status_code != 201:
            st.error(f"❌ ファイルアップロード失敗: {response.status_code}")
            st.write(response.text)
            st.stop()

        upload_file_id = response.json().get("id")
        st.write("✅ ファイルアップロード完了！")

        # **2. ワークフローを実行**
        st.write("🚀 画像処理を実行中...")
        workflow_payload = {
            "inputs": {
                "image": {
                    "transfer_method": "local_file",
                    "upload_file_id": upload_file_id,
                    "type": "image"
                }
            },
            "response_mode": "blocking",
            "user": data["user"]
        }

        workflow_response = requests.post(
            f"{DIFY_BASE_URL}/v1/workflows/run",
            headers=HEADERS,
            json=workflow_payload,
            timeout=60
        )

        if workflow_response.status_code != 200:
            st.error(f"❌ ワークフロー実行エラー: {workflow_response.status_code}")
            st.write(workflow_response.text)
            st.stop()

        result = workflow_response.json()
        status = result.get("data", {}).get("status")

        if status != "succeeded":
            st.error(f"❌ ワークフローが失敗しました (status: {status})")
            st.write(result)
            st.stop()

        # **3. 画像の URL を取得して表示**
        files = result["data"]["outputs"].get("files", [])
        if files and "url" in files[0]:
            image_url = files[0]["url"]
            full_image_url = f"{DIFY_BASE_URL}{image_url}" if image_url.startswith("/files/") else image_url

            st.write(f"画像URL: {full_image_url}")  # デバッグ用

            # **URL にアクセスできるかテスト**
            response = requests.get(full_image_url, headers=HEADERS)

            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                st.image(image, caption="処理後の画像", use_column_width=True)
            else:
                st.error("❌ 画像の取得に失敗しました。")
                st.write(f"エラーコード: {response.status_code}")
        else:
            st.warning("⚠ 画像の URL が取得できませんでした。")
            st.write(result)

    except requests.exceptions.Timeout:
        st.error("❌ リクエストがタイムアウトしました。ネットワークの状況を確認してください。")
    except Exception as e:
        st.error(f"❌ エラーが発生しました: {e}")
