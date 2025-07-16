import streamlit as st
from docx import Document
from io import BytesIO

# 페이지 설정
st.set_page_config(page_title="음악 문항 생성", layout="wide")

# CSS - 파스텔 블루 스타일
st.markdown("""
    <style>
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #e0f3ff !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# 왼쪽 UI
st.markdown("### 🎼 음악 문항 생성")
st.markdown("---")
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("생성할 유형 선택")

    # 문항 유형 선택
    st.markdown("#### ① 문항 유형 선택")
    question_types = st.multiselect(
        "문항 유형을 선택하세요",
        [
            "유형 1: 음악사 (텍스트)",
            "유형 2: 리듬/화성 (텍스트+청음)",
            "유형 3: 악보평가 (텍스트+악보)",
            "유형 4: 종합평가 (텍스트+청음+악보)"
        ]
    )

    # 정답 유형 선택
    st.markdown("#### ② 정답 유형 선택")
    answer_types = st.multiselect(
        "정답 유형을 선택하세요",
        [
            "유형 1: O/X 형",
            "유형 2: 객관식 (텍스트형)",
            "유형 3: 객관식 (악보형)",
            "유형 4: 주관식 (단답/서술형)"
        ]
    )

    # 버튼
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        generate = st.button("생성하기")
    with col_btn2:
        reset = st.button("선택사항 리셋")
    if reset:
        st.experimental_rerun()

# 오른쪽 결과 출력
with col2:
    st.subheader("생성 결과 보기")
    st.caption("🔹 *파일은 Word 형태로 다운로드하여 직접 편집 가능*")

    result_placeholder = st.empty()

    if generate:
        if not question_types:
            st.warning("문항 유형을 하나 이상 선택하세요.")
        else:
            # 문항 유형별 데모 로직 (CPU 기반)
            qtype = question_types[0]
            if "음악사" in qtype:
                question = (
                    "Q1. 다음 중 고전주의 음악에 속하는 작곡가는 누구인가요?\n"
                    "- A) 바흐\n- B) 모차르트\n- C) 드뷔시\n- D) 브람스\n정답: B"
                )
            elif "리듬" in qtype:
                question = (
                    "Q1. 음원에서 들리는 리듬 유형은 무엇인가요?\n"
                    "- A) 셔플 리듬\n- B) 보사노바\n- C) 마칭 드럼\n- D) 왈츠\n정답: D"
                )
            elif "악보평가" in qtype:
                question = (
                    "Q1. 아래 악보의 조성은 무엇인가요?\n"
                    "- A) 다장조\n- B) 사단조\n- C) 가단조\n- D) 바장조\n정답: A"
                )
            elif "종합평가" in qtype:
                question = (
                    "Q1. 악보와 음원을 참고하여 곡의 스타일로 가장 적절한 것은?\n"
                    "- A) 바로크\n- B) 고전주의\n- C) 낭만주의\n- D) 현대음악\n정답: C"
                )
            else:
                question = "지원되지 않는 문항 유형입니다."

            # 출력
            st.markdown("#### 예시 문항:")
            st.code(question, language="markdown")

            # Word 다운로드용 docx 생성
            doc = Document()
            doc.add_heading("🎼 문항 생성 결과", 0)
            doc.add_paragraph(question)
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="⬇ 다운로드",
                data=buffer,
                file_name="music_question.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        result_placeholder.info("왼쪽에서 항목을 선택하고 [생성하기] 버튼을 눌러주세요.")
