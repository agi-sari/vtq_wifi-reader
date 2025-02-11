import streamlit as st
import requests
import os

# ページの設定
st.set_page_config(page_title="Wi-Fi QR Generator", page_icon="📷", layout="centered")

# タイトル・説明文の表示
st.write("**Wi-Fi情報を含むオブジェクトを撮影してください**")

# セッションステートの初期化（撮影画像とQRコード画像を保持）
if 'captured_image' not in st.session_state:
    st.session_state['captured_image'] = None
if 'qr_code_image' not in st.session_state:
    st.session_state['qr_code_image'] = None

# 既に QR コード画像が取得済みの場合の処理
if st.session_state['qr_code_image']:
    # QRコード画像を表示
    st.image(st.session_state['qr_code_image'], caption="Wi-Fi QRコード", use_column_width=True)
    
    # 【QRを保存する】ボタン（st.download_button でローカル保存）
    st.download_button(
        label="QRを保存する",
        data=st.session_state['qr_code_image'],
        file_name="wifi_qr.png",
        mime="image/png"
    )
    
    # 【友だちに共有する（LINE）】ボタン  
    # ※QRコード画像が URL の場合はその URL を使って共有リンクを作成、画像バイトの場合は手動保存を促す
    qr_share_url = ""
    if isinstance(st.session_state['qr_code_image'], str):
        qr_share_url = st.session_state['qr_code_image']
    if qr_share_url:
        line_share_link = f"https://social-plugins.line.me/lineit/share?url={qr_share_url}"
        st.markdown(f"[友だちに共有する（LINE）]({line_share_link})", unsafe_allow_html=True)
    else:
        if st.button("友だちに共有する（LINE）"):
            st.info("画像を保存してLINEで共有してください")
    
    # 【ホームに戻る】ボタン（セッションをリセットして初期状態に戻す）
    if st.button("ホームに戻る"):
        st.session_state['captured_image'] = None
        st.session_state['qr_code_image'] = None
        st.experimental_rerun()

# まだ QR コード画像が取得されていない場合（撮影→送信のフロー）
else:
    # 画像が未撮影の場合
    if st.session_state['captured_image'] is None:
        # 「カメラを起動する」ボタンを表示
        if st.button("カメラを起動する"):
            st.session_state['camera_open'] = True
        # カメラ起動済みなら st.camera_input を表示
        if st.session_state.get('camera_open'):
            image_file = st.camera_input("写真を撮影してください", key="camera")
            if image_file is not None:
                # 撮影された画像をセッションに保存
                st.session_state['captured_image'] = image_file
                # プレビュー表示
                st.image(image_file, caption="撮影した画像", use_column_width=True)
    
    # 画像が撮影済みの場合は【送信する】【撮り直す】ボタンを表示
    if st.session_state['captured_image'] is not None and st.session_state.get('qr_code_image') is None:
        col1, col2 = st.columns(2)
        send_clicked = col1.button("送信する")
        retake_clicked = col2.button("撮り直す")
        
        if send_clicked:
            # 画像データ（バイト列）を取得
            img_bytes = st.session_state['captured_image'].getvalue()
            # Dify ワークフロー API のエンドポイント（下記はサンプルURL。実際のURLに置き換えてください）
            api_url = "http://elecnecta.jp/v1/workflows/run"
            # 環境変数から API キーを取得（デプロイ時に --set-env-vars で設定）
            api_key = os.getenv("DIFY_API_KEY")
            try:
                response = requests.post(
                    api_url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    files={"file": ("wifi.jpg", img_bytes, "image/jpeg")},
                    timeout=60
                )
            except Exception as e:
                st.error(f"APIリクエストに失敗しました: {e}")
                st.stop()
            if response.status_code != 200:
                st.error(f"API エラー: {response.status_code}")
            else:
                # API のレスポンスが JSON の場合（QRコード画像の URL が含まれるケース）
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    data = response.json()
                    qr_url = data.get("qr_url")
                    if qr_url:
                        # URL から実際の画像データを取得
                        qr_img_resp = requests.get(qr_url)
                        if qr_img_resp.status_code == 200:
                            st.session_state['qr_code_image'] = qr_img_resp.content
                        else:
                            st.error("QRコード画像の取得に失敗しました")
                    else:
                        st.error("QRコードのURLがレスポンスに含まれていません")
                else:
                    # レスポンスが直接画像バイナリの場合
                    st.session_state['qr_code_image'] = response.content
                # QRコード画像を取得したら再実行して表示画面へ
                st.experimental_rerun()
        
        if retake_clicked:
            # 撮影画像をクリアして再度カメラ起動状態に戻す
            st.session_state['captured_image'] = None
            st.session_state['camera_open'] = False
            st.experimental_rerun()
