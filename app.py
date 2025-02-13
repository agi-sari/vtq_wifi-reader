import streamlit as st
import requests
import os
import uuid
import time
import base64
from PIL import Image
from io import BytesIO
from streamlit_js_eval import streamlit_js_eval  # JavaScriptによるリロード用

# === Dify API の設定値 ===
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL")
DIFY_API_KEY = os.getenv("DIFY_API_KEY")
HEADERS = {"Authorization": f"Bearer {DIFY_API_KEY}"}

st.title("VTQ Wi-Fi Reader")
st.write("Wi-Fi情報が書かれたオブジェクトを撮影してください")

# セッション状態の初期化
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())  # ユーザーIDを生成

# エラー時のページリロード関数
def reload_page():
    """ページをリロードして初期状態に戻す"""
    streamlit_js_eval(js_expressions="parent.window.location.reload()")
    st.stop()

# ファイルアップロードオプション
with st.expander("撮影またはアップロード", expanded=False):
    input_method = st.radio("", ["カメラで撮影", "ファイルをアップロード"])

    if input_method == "カメラで撮影":
        st.session_state.uploaded_file = st.camera_input("")
    elif input_method == "ファイルをアップロード":
        st.session_state.uploaded_file = st.file_uploader(
            "ファイルをアップロード", 
            type=["png", "jpg", "jpeg", "webp"]
        )

# アップロードファイルの取得
uploaded_file = st.session_state.uploaded_file
if uploaded_file:
    try:
        st.write("📤 画像をアップロード中...")

        # MIME タイプ取得
        mime_type = uploaded_file.type if uploaded_file.type else "image/png"
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), mime_type)}
        data = {"user": st.session_state.user_id}

        # ファイルアップロード
        response = requests.post(
            f"{DIFY_BASE_URL}/v1/files/upload",
            headers=HEADERS,
            files=files,
            data=data,
            timeout=60
        )

        if response.status_code != 201:
            st.error(f"アップロード失敗: {response.status_code}\n{response.json().get('message', '不明なエラー')}")
            time.sleep(3)
            reload_page()

        upload_file_id = response.json().get("id")

        # ワークフロー実行
        st.write("🚀 画像処理を実行！")
        workflow_payload = {
            "inputs": {
                "image": {
                    "transfer_method": "local_file",
                    "upload_file_id": upload_file_id,
                    "type": "image"
                }
            },
            "response_mode": "blocking",
            "user": st.session_state.user_id
        }

        workflow_response = requests.post(
            f"{DIFY_BASE_URL}/v1/workflows/run",
            headers=HEADERS,
            json=workflow_payload,
            timeout=60
        )

        if workflow_response.status_code != 200:
            st.error(f"処理失敗: {workflow_response.status_code}\n{workflow_response.json().get('message', '不明なエラー')}")
            time.sleep(3)
            reload_page()

        result = workflow_response.json()
        status = result.get("data", {}).get("status")

        if status != "succeeded":
            st.error(f"画像処理に失敗しました。(status: {status})")
            time.sleep(3)
            reload_page()

        # 生成された画像URLの取得
        files_output = result["data"]["outputs"].get("files", [])

        if not files_output or "url" not in files_output[0]:
            st.warning("画像のURLが取得できませんでした。")
            time.sleep(3)
            reload_page()

        image_url = files_output[0]["url"]
        full_image_url = (
            f"{DIFY_BASE_URL}{image_url}"
            if image_url.startswith("/files/")
            else image_url
        )

        # 画像取得テスト
        response_img = requests.get(full_image_url, headers=HEADERS)
        if response_img.status_code != 200:
            st.error(f"QRコードの取得に失敗しました: {response_img.status_code}")
            time.sleep(3)
            reload_page()

        # 画像を60%のサイズにリサイズ
        image = Image.open(BytesIO(response_img.content))
        width, height = image.size
        new_size = (int(width * 0.6), int(height * 0.6))
        resized_image = image.resize(new_size, Image.LANCZOS)

        # 画像をbase64にエンコードしてHTMLで表示（中央揃え）
        img_bytes = BytesIO()
        resized_image.save(img_bytes, format="PNG")
        encoded_img = base64.b64encode(img_bytes.getvalue()).decode()

        img_html = f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{encoded_img}" style="max-width: 600%; height: auto;">
        </div>
        """
        st.markdown(img_html, unsafe_allow_html=True)

    except requests.exceptions.Timeout:
        st.error("リクエストがタイムアウトしました。")
        time.sleep(3)
        reload_page()

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        time.sleep(3)
        reload_page()
