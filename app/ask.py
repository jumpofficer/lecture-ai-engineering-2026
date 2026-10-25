"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    uv run python -m app.ask --interactive
    uv run python -m app.ask --interactive "LoRAとは何ですか？"

ツールを持たない「素の」呼び出し。--interactive では会話履歴を保って質問を続けられる。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors
from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def create_chat():
    client = genai.Client(api_key=get_api_key())
    return client, client.chats.create(model=MODEL)


def ask(question: str, chat=None) -> str:
    if chat is None:
        client, chat = create_chat()
    response = chat.send_message(question)

    # TODO(第1回 演習): response.usage_metadata から
    #   入力トークン数と出力トークン数を表示してみよう（Copilotに頼んでよい）

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?")
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="会話履歴を保ったまま質問を続ける",
    )
    args = parser.parse_args()

    question = args.question
    if not args.interactive and question is None:
        question = DEFAULT_QUESTION

    print(f"[model] {MODEL}")
    try:
        # Chat は Client の HTTP 接続を使うため、会話中は Client も保持する。
        client, chat = create_chat()
        if question is not None:
            print(f"[質問] {question}\n")
            print(ask(question, chat))

        if args.interactive:
            while True:
                try:
                    follow_up = input("\n質問（終了するには空行）> ")
                except EOFError:
                    break
                if not follow_up.strip():
                    break
                print(f"\n[質問] {follow_up}\n")
                print(ask(follow_up, chat))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
