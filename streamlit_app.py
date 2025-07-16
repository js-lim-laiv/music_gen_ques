import streamlit as st
from io import BytesIO
from docx import Document

# 페이지 설정
st.set_page_config(page_title="음악 문항 생성", layout="wide")

# 좌측 영역 - 선택
st.markdown("### 🎼 음악 문항 생성")
st.markdown("---")
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("생성할 유형 선택")

    # 문항 유형 선택
    st.markdown("#### ① 문항 유형 선택")
    question_types = st.multiselect(
        label="문항 유형을 선택하세요",
        options=[
            "유형 1: 음악사 (텍스트)",
            "유형 2: 리듬/화성 (텍스트+청음)",
            "유형 3: 악보평가 (텍스트+악보)",
            "유형 4: 종합평가 (텍스트+청음+악보)"
        ]
    )

    # 정답 유형 선택
    st.markdown("#### ② 정답 유형 선택")
    answer_types = st.multiselect(
        label="정답 유형을 선택하세요",
        options=[
            "유형 1: O/X 형",
            "유형 2: 객관식 (텍스트형)",
            "유형 3: 객관식 (악보형)",
            "유형 4: 주관식 (단답/서술형)"
        ]
    )

    # 버튼 영역
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        generate = st.button("생성하기")
    with col_btn2:
        reset = st.button("선택사항 리셋")

    if reset:
        st.experimental_rerun()

with col2:
    st.subheader("생성 결과 보기")
    st.caption("🔹 *파일은 Word 형태로 다운로드하여 직접 편집 가능*")
    result_placeholder = st.empty()

    if generate:
        doc = Document()
        doc.add_heading("🎼 문항 생성 결과", 0)

        # 예시 문항 구성
        example_question = (
            "Q1. 다음 중 음악사적으로 바로크 시대에 해당하는 작곡가는 누구인가요?\n"
            "- A) 모차르트\n"
            "- B) 바흐\n"
            "- C) 베토벤\n"
            "- D) 쇼팽\n"
            "정답: B"
        )

        # Streamlit 화면 출력
        st.markdown("#### 예시 문항:")
        st.code(example_question, language="markdown")

        # Word 파일 생성
        doc.add_paragraph(example_question)
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