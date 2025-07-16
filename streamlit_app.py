import streamlit as st
from io import BytesIO
from docx import Document
import random
from transformers import pipeline

# LLM 모델 초기화 (한국어 특화 모델 사용)
try:
    text_generator = pipeline("text-generation", model="beomi/KoAlpaca-Polyglot-12.8B")
    gpt_ready = True
except:
    gpt_ready = False

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

    if audio_file:
        st.audio(audio_file, format='audio/wav' if audio_file.name.endswith(".wav") else 'audio/mp3')

    def generate_llm_question(prompt):
        if not gpt_ready:
            return "⚠️ 모델이 준비되지 않아 예시 문항을 사용합니다."
        try:
            result = text_generator(prompt, max_length=300, do_sample=True, temperature=0.8)[0]["generated_text"]
            return result
        except Exception as e:
            return f"⚠️ LLM 생성 오류: {str(e)}"

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
            # 정답 유형 기반 프롬프트 설정
            if answer_type == "O/X":
                prompt = "고전 음악사와 관련된 O/X 문제를 한국어로 만들어줘. 질문과 정답(O 또는 X)을 명확하게 포함해줘."
            elif "객관식" in answer_type:
                prompt = ("고전 음악사 관련 객관식 문제를 한국어로 생성해줘. "
                          "보기 A) B) C) D) 형식과 정답 표시도 포함해줘.")
            elif "서술형" in answer_type:
                prompt = "고전 음악사에 대한 서술형 문항을 생성해줘. 질문은 명확하게, 정답 예시는 한 문장으로."
            else:
                prompt = "고전 음악사 관련 문항을 생성해줘."

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
