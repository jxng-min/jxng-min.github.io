# tools/refine_ai.py
import sys
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from common import build_post_path

def main():
    if len(sys.argv) != 2:
        print('사용법: py tools/refine_ai.py <제목>')
        sys.exit(1)

    load_dotenv()

    title = sys.argv[1].strip()
    post_path = build_post_path(title)

    if not os.getenv('OPENAI_API_KEY'):
        raise RuntimeError('OPENAI_API_KEY가 .env에 설정되지 않았습니다.')

    if not post_path.exists():
        raise FileNotFoundError(f'대상 파일이 없습니다. 먼저 draft_ai.py로 생성하세요: {post_path}')

    original_md = post_path.read_text(encoding='utf-8')

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "너는 게임 개발자 기술 블로그 글을 퇴고/리라이트하는 편집자다. "
         "과장하지 말고, 흐름과 정확성을 개선하며, 독자가 따라하기 쉽게 만든다."),
        ("user",
         """아래는 Jekyll 포스트 초안 마크다운 전체다. 이 글을 '퇴고(refine)'해서 결과를 **마크다운 전체**로 다시 출력해줘.

        [최우선 규칙]
        1) front matter(---로 감싼 YAML)는 반드시 유지한다.
        2) front matter에서 `layout`, `title`, `date` 값은 절대 변경하지 마라.
        3) front matter의 다른 키(`excerpt`, `tags`, `image`)는 비어있거나 부적절하면 개선해도 된다.
        - excerpt: 한 줄 요약(따옴표 권장)
        - tags: Unity/Cocos/Algorithm/Math/ETC 중에서 3~6개로 정리
        4) 본문은 한국어, 게임 개발자 기술 블로그 톤을 유지한다.
        5) 결과는 **파일에 바로 덮어쓸 수 있는 완성본**이어야 한다(부분 출력 금지).

        [퇴고 목표]
        - 글의 흐름을 자연스럽게 (서론→개념→적용→주의점→마무리)
        - 강조할 단어는 Bold 처리, 프로그래밍 언어의 키워드거나, 게임 엔진의 키워드인 경우 ``로 코드블럭 처리 
        - 중복/군더더기 제거
        - 어색한 표현/맞춤법/띄어쓰기 수정
        - 용어/영문 표기 통일 (예: Update/FixedUpdate, State Machine/FSM 등)
        - 핵심 요약 섹션(불릿) 추가 (본문 초반에 추천)
        - 필요한 경우 작은 예시 코드/의사코드 추가(과도하게 길게는 X)
        - 헤더 계층을 ##, ###로 정리

        [추가 조건]
        - 본문(프론트 매터 제외) 900자 이상 유지
        - 코드블록은 ``` 로 감싸기
        - 과장/단정 표현 완화 (예: "무조건" → "대부분", "항상" → "종종")

        [입력 문서 시작]
        {doc}
        [입력 문서 끝]
        """)
    ])

    llm = ChatOpenAI(model='gpt-4o', temperature=0.2)
    chain = prompt | llm | StrOutputParser()

    refined_md = chain.invoke({"doc": original_md})

    post_path.write_text(refined_md, encoding='utf-8')
    print(f"✅ 블로그 퇴고 완료: {post_path}")

if __name__ == "__main__":
    main()