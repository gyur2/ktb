import requests
import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="Fruit & Veg Classifier", page_icon="🍎")

st.title("Fruit & Vegetable Classification")
st.write("로컬 FastAPI 서버에 이미지를 보내서 과일/야채를 분류합니다.")

# 백엔드 URL
BACKEND_URL = "http://127.0.0.1:8000/predict-fruit-veg"

# 이미지 업로더
image_file = st.file_uploader("이미지 파일을 선택하세요 (jpg / png)", type=["jpg", "jpeg", "png"])

# 예측 버튼
if st.button("Predict"):
    if image_file is None:
        st.warning("먼저 이미지를 업로드해주세요.")
    else:
        # 업로드된 이미지를 화면에 보여주기
        image_bytes = image_file.read()
        st.image(image_bytes, width=240, caption="Input Image")

        # FastAPI로 보낼 multipart/form-data 구성
        files = {
            "file": (
                image_file.name,
                image_bytes,
                image_file.type or "application/octet-stream",
            )
        }

        try:
            st.write("⏳ 서버에 요청 중...")
            res = requests.post(BACKEND_URL, files=files, timeout=10)

            st.write("Status code:", res.status_code)

            # 상태 코드가 200이 아니면 에러
            if res.status_code != 200:
                try:
                    err = res.json()
                    st.error(f"요청 실패: {err.get('detail', res.text)}")
                except Exception:
                    st.error(f"요청 실패: {res.text}")
            else:
                data = res.json()
                st.success(f"예측 결과: **{data['top1_label']}** "
                           f"(score: {data['top1_score']:.4f})")

                st.subheader("클래스별 확률")
                probs = data.get("probabilities", {})
                # 확률을 내림차순 정렬해서 보기 좋게 표시
                for label, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"- **{label}**: {prob:.4f}")

        except requests.exceptions.RequestException as e:
            st.error(f"요청 중 네트워크 오류가 발생했습니다: {e}")
        except Exception as e:
            st.error(f"예상치 못한 오류가 발생했습니다: {e}")
