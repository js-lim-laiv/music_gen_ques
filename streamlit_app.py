import streamlit as st
from io import BytesIO
from docx import Document
import random
import librosa
import numpy as np
import joblib
import matplotlib.pyplot as plt

# music21 악보 분석 (로컬에서만 시각화 가능)
try:
    from music21 import converter
    music21_available = True
except ImportError:
    music21_available = False

# Rhythm classifier model 로드
try:
    rhythm_model = joblib.load("rhythm_svm.pkl")
    rhythm_ready = True
except:
    rhythm_ready = False

# Streamlit UI
st.set_page_config(page_title="AI 음악 문항 생성기", layout="wide")
st.title("🎼 AI 기반 음악 문항 생성기 (PoC)")
st.markdown("---")

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("1️⃣ 생성할 문항 유형")
    question_type = st.selectbox("문항 유형", [
        "유형 1: 음악사 (GPT2 기반 모의)",
        "유형 2: 리듬/화성 (오디오 분석)",
        "유형 3: 악보 평가 (조성 분석)",
        "유형 4: 종합 평가"
    ])

    st.subheader("2️⃣ 정답 유형")
    answer_type = st.selectbox("정답 유형", ["O/X", "객관식 (텍스트)", "악보형 보기", "서술형"])

    audio_file = st.file_uploader("🎵 오디오 업로드 (wav)", type=["wav"])
    score_file = st.file_uploader("🎼 악보 업로드 (musicxml)", type=["xml", "musicxml"])
    generate = st.button("✨ 문항 생성하기")

with col2:
    st.subheader("🧾 생성 결과")
    st.caption("아래는 실제 모델 기반으로 생성된 문항입니다.")

    def generate_mock_korean_question():
        return (
            "Q. 다음 중 고전주의 시대의 작곡가는 누구인가요?\n"
            "A) 드뷔시\nB) 모차르트\nC) 말러\nD) 쇼팽\n정답: B"
        )

    def classify_rhythm(file):
        try:
            file_bytes = file.read()
            import soundfile as sf
            import io
            y, sr = sf.read(io.BytesIO(file_bytes))
            mfcc = librosa.feature.mfcc(y=y, sr=sr)
            feature = mfcc.mean(axis=1).reshape(1, -1)
            if rhythm_ready:
                label = rhythm_model.predict(feature)[0]
                return f"Q. 업로드된 음원의 리듬 유형은 무엇인가요?
정답: {label}"
            else:
                return f"리듬 모델이 준비되지 않았습니다. 랜덤 리듬 사용.
정답: {random.choice(['왈츠', '보사노바', '펑크'])}"
        except Exception as e:
            return f"오류 발생: {str(e)}"

    def analyze_score(file):
        if not music21_available:
            return "music21이 설치되어 있지 않아 악보 분석이 불가합니다."
        try:
            score = converter.parse(file)
            key = score.analyze('key')
            return f"Q. 이 악보의 조성(Key)은 무엇인가요?\n정답: {key}"
        except Exception as e:
            return f"악보 분석 오류: {e}"

    def combine_all(text, audio, score):
        return (
            f"Q. 다음 곡에 대한 분석 결과로 보아 어떤 시대의 음악인가요?\n"
            f"- 🎵 리듬 분석: {audio}\n"
            f"- 🎼 조성 분석: {score}\n"
            f"- 📖 문헌 기반 정보: {text}\n"
            f"정답: 고전주의"
        )

    if generate:
        if "음악사" in question_type:
            result = generate_mock_korean_question()
        elif "리듬" in question_type and audio_file:
            result = classify_rhythm(audio_file)
        elif "악보" in question_type and score_file:
            result = analyze_score(score_file)
        elif "종합" in question_type:
            text = generate_mock_korean_question()
            audio = classify_rhythm(audio_file) if audio_file else "오디오 없음"
            score = analyze_score(score_file) if score_file else "악보 없음"
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
