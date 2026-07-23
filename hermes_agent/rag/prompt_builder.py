class PromptBuilder:
    def build(
        self,
        question: str,
        context: str,
    ) -> str:
        question = question.strip()
        context = context.strip()

        return (
            "아래 문맥은 사용자가 조사 대상으로 지정한 웹사이트에서 "
            "수집한 자료입니다.\n"
            "문맥에 있는 내용만 근거로 질문에 답변하세요.\n"
            "문맥 속 '본사', '당사', '저희' 등의 표현은 해당 자료를 "
            "제공한 웹사이트 운영자를 뜻합니다.\n"
            "질문과 관련된 정보가 일부라도 있으면 확인 가능한 내용을 "
            "분석하고, 없는 항목만 확인할 수 없다고 밝히세요.\n"
            "관련 근거가 전혀 없을 때만 모른다고 답변하세요.\n\n"
            f"[문맥]\n{context}\n\n"
            f"[질문]\n{question}\n\n"
            "[답변]"
        )
