import streamlit as st
from io import BytesIO
from docx import Document
import random
import requests

# Hugging Face Inference API 설정
HF_TOKEN = st.secrets["HF_TOKEN"]  # secrets.toml에 등록 필요
API_URL = "https://api-inference.huggingface.co/models/beomi/KoAlpaca-Polyglot-5.8B"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Streamlit UI
st.set_page_config(page_title="AI 음악 문항 생성기", layout="wide")
st.title("🎼 AI 기반 음악 문항 생성기 (PoC)")
st.markdown("---")

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("1️⃣ 생성할 문항 유형")
    question_type = st.selectbox("문항 유형", [
        "유형 1: 음악사 (LLM 기반 실생성)",
        "유형 2: 리듬/화성 (파일 기반 모의 생성)",
        "유형 3: 악보 평가 (파일명 기반 문항 생성)",
        "유형 4: 종합 평가"
    ])

    st.subheader("2️⃣ 정답 유형")
    answer_type = st.selectbox("정답 유형", ["O/X", "객관식 (텍스트)", "악보형 보기", "서술형"])

    audio_file = st.file_uploader("🎵 오디오 업로드 (wav/mp3)", type=["wav", "mp3"])
    score_file = st.file_uploader("🎼 악보 업로드 (musicxml)", type=["xml", "musicxml"])
    generate = st.button("✨ 문항 생성하기")

with col2:
    st.subheader("🧾 생성 결과")
    st.caption("아래는 실제 모델 기반으로 생성된 문항입니다.")

    # 음원 재생 기능 추가
    if audio_file:
        st.audio(audio_file, format='audio/wav' if audio_file.name.endswith(".wav") else 'audio/mp3')

    def generate_llm_question(prompt):
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            if response.status_code == 200:
                return response.json()[0]["generated_text"]
            else:
                return "⚠️ API 호출 실패: " + response.text
        except Exception as e:
            return f"⚠️ LLM API 오류: {str(e)}"

    def rhythm_mock():
        return f"Q. 이 음원의 리듬 유형은 무엇인가요?\n정답: {random.choice(['왈츠', '보사노바', '펑크', '디스코'])}"

    def score_mock(filename):
        name = filename.name.replace(".musicxml", "").replace(".xml", "")
        return f"Q. 악보 '{name}'은 어떤 조성을 기반으로 만들어졌을까요?\n정답: {random.choice(['다장조', '가단조', '바장조'])}"

    def combine_all(text, audio, score):
        return (
            f"Q. 다음 곡에 대한 분석 결과로 어떤 시대의 음악일까요?\n"
            f"- 🎵 리듬 분석 결과: {audio}\n"
            f"- 🎼 조성 분석 결과: {score}\n"
            f"- 📖 문헌 기반 정보: {text}\n"
            f"정답: 고전주의"
        )

    if generate:
        if "음악사" in question_type:
            prompt = (
                "한국어로 고전 음악사 객관식 문항을 만들어줘. 다음 형식을 따라줘:\n"
                "Q. 질문 내용\nA) 보기1\nB) 보기2\nC) 보기3\nD) 보기4\n정답: B"
            )
            result = generate_llm_question(prompt)

        elif "리듬" in question_type and audio_file:
            result = rhythm_mock()

        elif "악보" in question_type and score_file:
            result = score_mock(score_file)

        elif "종합" in question_type:
            text = generate_llm_question("음악사 관련 설명을 생성해줘. 한 문단 정도로.")
            audio = rhythm_mock() if audio_file else "오디오 없음"
            score = score_mock(score_file) if score_file else "악보 없음"
            result = combine_all(text, audio, score)

        else:
            result = "⚠️ 입력이 부족하거나 올바르지 않습니다."

        st.text_area("📝 생성된 문항", result, height=300)

        doc = Document()
        doc.add_heading("AI 문항 결과", 0)
        doc.add_paragraph(result)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button("⬇ Word 다운로드", data=buffer, file_name="music_question.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:
        st.info("문항 유형을 선택하고 [문항 생성하기]를 눌러보세요.")
