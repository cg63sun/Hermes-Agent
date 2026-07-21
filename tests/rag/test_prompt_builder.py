from hermes_agent.rag.prompt_builder import PromptBuilder


def test_build_prompt() -> None:
    builder = PromptBuilder()

    prompt = builder.build(
        question="Python이란 무엇인가요?",
        context="Python은 프로그래밍 언어입니다.",
    )

    assert prompt == (
        "아래 문맥을 참고하여 질문에 답변하세요.\n"
        "문맥에 답이 없다면 모른다고 답변하세요.\n\n"
        "[문맥]\n"
        "Python은 프로그래밍 언어입니다.\n\n"
        "[질문]\n"
        "Python이란 무엇인가요?\n\n"
        "[답변]"
    )


def test_build_prompt_strips_whitespace() -> None:
    builder = PromptBuilder()

    prompt = builder.build(
        question="  질문입니다.  ",
        context="  문맥입니다.  ",
    )

    assert "[문맥]\n문맥입니다." in prompt
    assert "[질문]\n질문입니다." in prompt


def test_build_prompt_with_empty_context() -> None:
    builder = PromptBuilder()

    prompt = builder.build(
        question="질문입니다.",
        context="",
    )

    assert "[문맥]\n\n" in prompt
    assert "[질문]\n질문입니다." in prompt
