from hermes_agent.rag.prompt_builder import PromptBuilder


def test_build_prompt() -> None:
    builder = PromptBuilder()

    prompt = builder.build(
        question="Python이란 무엇인가요?",
        context="Python은 프로그래밍 언어입니다.",
    )

    assert prompt == (
        "아래 문맥은 사용자가 조사 대상으로 지정한 웹사이트에서 "
        "수집한 자료입니다.\n"
        "문맥에 있는 내용만 근거로 질문에 답변하세요.\n"
        "문맥 속 '본사', '당사', '저희' 등의 표현은 해당 자료를 "
        "제공한 웹사이트 운영자를 뜻합니다.\n"
        "질문과 관련된 정보가 일부라도 있으면 확인 가능한 내용을 "
        "분석하고, 없는 항목만 확인할 수 없다고 밝히세요.\n"
        "관련 근거가 전혀 없을 때만 모른다고 답변하세요.\n\n"
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


def test_build_prompt_explains_website_research_rules() -> None:
    builder = PromptBuilder()

    prompt = builder.build(
        question="경쟁사의 강점을 분석하세요.",
        context="본사는 반응형 홈페이지를 제작합니다.",
    )

    assert "웹사이트에서 수집한 자료" in prompt
    assert "웹사이트 운영자를 뜻합니다" in prompt
    assert "정보가 일부라도 있으면" in prompt
    assert "관련 근거가 전혀 없을 때만" in prompt
