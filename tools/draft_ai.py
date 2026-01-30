from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from common import build_post_path, POSTS_DIR
import sys
import os

def main():
    if len(sys.argv) > 2:
        print('사용법: py tools/draft_ai.py <제목>')
        sys.exit(1)

    load_dotenv()
    
    title = sys.argv[1].strip()
    post_path = build_post_path(title)
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    if not os.getenv('OPENAI_API_KEY'):
        raise RuntimeError('OPENAI_API_KEY가 .env에 설정되지 않았습니다.')
    
    prompt = ChatPromptTemplate.from_messages([
        ('system', '너는 게임 개발자 기술 블로그의 포스트 초안 생성기다. 과장하지 말고 상용적으로 쓴다.'),
        ('user', '''
        제목: {title}
         
        아래 조건을 지켜서 Jekyll 포스트 초안을 '마크다운 전체'로 출력해줘.
         
         - 맨 위에 front matter를 포함한다. (주의: 반드시 ---로 시작과 끝을 감싸기)
            front matter 예시:
            ---
            layout: post
            title: 입력 제목 그대로
            date: 오늘 날짜 12:00:00 +0900
            excerpt: 한 줄 요약
            tags: Unity/Cocos/Algorithm/Math/ETC 중 어울리는 태그를 설정한다. (복수 가능)
            image: 비워도 됨
            ---
         
        본문 구조:
        1) 서론(문제/배경)
        2) 핵심 개념
        3) 구현/적용(코드나 의사코드 포함)
        4) 실수/주의점
        5) 마무리(게임 개발에서 어떻게 쓰는가)        
         
        추가 조건:
        - 900자 이상
        - 헤더는 ##, ### 사용
        - 코드블록은 ``` 로 감싸기

        ''')
    ])

    llm = ChatOpenAI(model='gpt-4o', temperature=0.3)
    chain = prompt | llm | StrOutputParser()
    
    md = chain.invoke({'title': title})

    post_path.write_text(md, encoding="utf-8")
    print(f"✅ 블로그 초안 생성 완료: {post_path}")    


if __name__ == "__main__":
    main()