import streamlit as st
from io import BytesIO
from docx import Document
import random

# Optional: For audio processing
import librosa
import numpy as np

# Optional: For score processing (if music21 installed)
try:
    from music21 import converter
    music21_available = True
except ImportError:
    music21_available = False

# Optional: For text generation (Open Source, CPU-capable)
try:
    from transformers import pipeline
    llm = pipeline("text-generation", model="gpt2", device=-1)
    gpt_available = True
except Exception:
    gpt_available = False

# Streamlit app
st.set_page_config(page_title="AI 음악 문항 생성기", layout="wide")
st.title("🎼 AI 기반 음악 문항 생성기")
st.markdown("---")

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("1️⃣ 생성할 문항 유형")
    question_type = st.selectbox("문항 유형", [
        "유형 1: 음악사 (텍스트 기반)",
        "유형 2: 리듬/화성 (청음 기반)",
        "유형 3: 악보 평가 (조성 분석)",
        "유형 4: 종합 평가 (복합 추론)"
    ])

    st.subheader("2️⃣ 정답 유형")
    answer_type = st.selectbox("정답 유형", ["O/X", "객관식 (텍스트)", "악보형 보기", "서술형"])

    # 파일 업로드
    audio_file = st.file_uploader("🎵 오디오 업로드 (wav)", type=["wav"])
    score_file = st.file_uploader("🎼 악보 업로드 (musicxml)", type=["xml", "musicxml"])

    generate = st.button("✨ 문항 생성하기")

with col2:
    st.subheader("🧾 생성 결과")
    st.caption("선택한 문항 유형과 입력 데이터를 바탕으로 AI가 문항을 생성합니다.")

    def generate_text_question():
        if gpt_available:
            result = llm("고전주의 작곡가 객관식 문항 생성", max_length=100, num_return_sequences=1)[0]['generated_text']
            return result.strip()
        else:
            return "Q. 다음 중 고전주의 작곡가는 누구인가요?\nA) 바흐\nB) 모차르트\nC) 드뷔시\nD) 브람스\n정답: B"

    def analyze_audio(file):
        try:
            y, sr = librosa.load(file, sr=22050)
            mfcc = librosa.feature.mfcc(y=y, sr=sr)
            rhythm = random.choice(["왈츠", "보사노바", "마칭 드럼", "셔플"])
            return f"Q. 이 음원의 리듬 유형은 무엇인가요?\n정답: {rhythm}"
        except Exception as e:
            return f"오디오 분석 오류: {e}"

    def analyze_score(file):
        if not music21_available:
            return "music21 미설치. 악보 분석 불가."
        try:
            score = converter.parse(file)
            k = score.analyze('key')
            return f"Q. 이 악보의 조성은 무엇인가요?\n정답: {k}"
        except Exception as e:
            return f"악보 분석 오류: {e}"

    def combine_all(text, audio, score):
        return (
            f"Q. 다음 곡의 종합 분석 결과, 가장 적절한 시대는 무엇인가요?\n"
            f"- 텍스트 분석 결과: 고전주의\n"
            f"- 리듬 분석 결과: {audio}\n"
            f"- 조성 분석 결과: {score}\n정답: 고전주의"
        )

    if generate:
        if "음악사" in question_type:
            result = generate_text_question()
        elif "리듬" in question_type and audio_file:
            result = analyze_audio(audio_file)
        elif "악보 평가" in question_type and score_file:
            result = analyze_score(score_file)
        elif "종합 평가" in question_type:
            text = generate_text_question()
            audio = analyze_audio(audio_file) if audio_file else "(오디오 없음)"
            score = analyze_score(score_file) if score_file else "(악보 없음)"
            result = combine_all(text, audio, score)
        else:
            result = "유효한 입력을 선택해주세요."

        st.text_area("📝 생성된 문항", result, height=250)

        # Word 다운로드 기능
        doc = Document()
        doc.add_heading("AI 문항 결과", 0)
        doc.add_paragraph(result)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button("⬇ Word 다운로드", data=buffer, file_name="music_question.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:
        st.info("왼쪽에서 문항 유형을 선택하고 문항을 생성해보세요.")
