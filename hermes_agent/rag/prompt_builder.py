class PromptBuilder:
    def build(
        self,
        question: str,
        context: str,
    ) -> str:
        question = question.strip()
        context = context.strip()

        return (
            "아래 문맥을 참고하여 질문에 답변하세요.\n"
            "문맥에 답이 없다면 모른다고 답변하세요.\n\n"
            f"[문맥]\n{context}\n\n"
            f"[질문]\n{question}\n\n"
            "[답변]"
        )
