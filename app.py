import streamlit as st
import requests
import os
import uuid
from PIL import Image
from io import BytesIO

# === Dify APIの設定値 ===
DIFY_BASE_URL = "https://elecnecta.jp"
DIFY_API_KEY = os.getenv("DIFY_API_KEY")
HEADERS = {"Authorization": f"Bearer {DIFY_API_KEY}"}

st.title("カメラ入力 & 画像処理アプリ")

# session_state の初期化
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# 折り畳み（expander）内で、ユーザーに撮影orアップロードを選ばせる
with st.expander("画像を入力する", expanded=False):
    input_method = st.radio("入力方法を選択してください", ["カメラで撮影", "ファイルをアップロード"])

    # カメラ撮影
    if input_method == "カメラで撮影":
        st.session_state.uploaded_file = st.camera_input("こちらで撮影してください")

    # ファイルアップロード
    elif input_method == "ファイルをアップロード":
        st.session_state.uploaded_file = st.file_uploader("ファイルをアップロード", type=["png","jpg","jpeg","webp"])

# 画像が用意できたら処理を実行
uploaded_file = st.session_state.uploaded_file
if uploaded_file:
    try:
        st.write("📤 画像をアップロード中...")
        mime_type = uploaded_file.type if uploaded_file.type else "image/png"
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), mime_type)}
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

        # ワークフローを実行
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

        # 生成された画像URLを取得して表示
        files_output = result["data"]["outputs"].get("files", [])
        if files_output and "url" in files_output[0]:
            image_url = files_output[0]["url"]
            # URLが /files/ で始まる場合はフルパスに修正
            full_image_url = (
                f"{DIFY_BASE_URL}{image_url}"
                if image_url.startswith("/files/")
                else image_url
            )

            # 画像取得テスト
            response_img = requests.get(full_image_url, headers=HEADERS)
            if response_img.status_code == 200:
                image = Image.open(BytesIO(response_img.content))

                # 画像を 60% に縮小
                width, height = image.size
                new_size = (int(width * 0.6), int(height * 0.6))
                resized_image = image.resize(new_size, Image.ANTIALIAS)

                # 中央揃えで表示
                st.markdown(
                    f"<div style='display: flex; justify-content: center;'>"
                    f"<img src='{full_image_url}' width='{new_size[0]}'></div>",
                    unsafe_allow_html=True
                )
            else:
                st.error("❌ 画像の取得に失敗しました。")
                st.write(f"エラーコード: {response_img.status_code}")
        else:
            st.warning("⚠ 画像の URL が取得できませんでした。")
            st.write(result)

    except requests.exceptions.Timeout:
        st.error("❌ リクエストがタイムアウトしました。")
    except Exception as e:
        st.error(f"❌ エラーが発生しました: {e}")
