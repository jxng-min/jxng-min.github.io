import sys
import subprocess

def run(cmd: list[str]):
    print("> " + " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    if len(sys.argv) != 2:
        print('사용법: py tools/ai_pipeline.py <제목>')
        sys.exit(1)

    title = sys.argv[1].strip()

    py = sys.executable

    run([py, "tools/draft_ai.py", title])
    run([py, "tools/refine_ai.py", title])
    run([py, "tools/revise_ai.py", title])

    print("✅ AI 파이프라인 완료 (draft → refine → revise)")

if __name__ == "__main__":
    main()