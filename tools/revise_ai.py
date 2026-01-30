# tools/revise_ai.py
import sys
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from common import build_post_path

def main():
    if len(sys.argv) != 2:
        print('사용법: py tools/revise_ai.py <제목>')
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
         "너는 게임 개발자 기술 블로그 글의 최종 교정(revise)을 담당하는 교정자다. "
         "문장과 표기를 다듬되, 내용/구조를 과하게 바꾸지 않는다."),
        ("user",
         """아래는 Jekyll 포스트 마크다운 전체다. 이 글을 '최종 교정(revise)'해서 **마크다운 전체**로 다시 출력해줘.

        [최우선 규칙]
        1) front matter(---로 감싼 YAML)는 반드시 유지한다.
        2) front matter에서 `layout`, `title`, `date` 값은 절대 변경하지 마라.
        3) front matter의 다른 키(`excerpt`, `tags`, `image`)도 가능하면 유지하되,
        명백히 비어있거나 잘못된 경우에만 최소 수정으로 바로잡아라.
        4) 결과는 **파일에 바로 덮어쓸 수 있는 완성본**이어야 한다(부분 출력 금지).
        5) 한국어 유지.

        [교정 체크리스트]
        - 맞춤법/띄어쓰기/오타
        - 어색한 표현 자연스럽게
        - 같은 용어/영문 표기 통일 (예: FixedUpdate/Update, Finite State Machine/FSM 등)
        - 지나치게 단정적인 표현 완화 (필요 시 최소 수정)
        - 링크/코드블록/마크다운 깨짐 여부 확인
        - 불필요한 이모지/과도한 감탄 표현 제거

        [절대 하지 말 것]
        - 글의 큰 구조(섹션 구성)를 바꾸지 말 것
        - 예시 코드의 의미를 바꾸는 리팩터링 금지
        - 새 주제 추가 금지
        - 분량을 크게 늘리거나 줄이지 말 것

        [입력 문서 시작]
        {doc}
        [입력 문서 끝]
        """)
    ])

    llm = ChatOpenAI(model='gpt-4o', temperature=0.1)
    chain = prompt | llm | StrOutputParser()

    revised_md = chain.invoke({"doc": original_md})

    post_path.write_text(revised_md, encoding='utf-8')
    print(f"✅ 블로그 최종 교정 완료: {post_path}")

if __name__ == "__main__":
    main()