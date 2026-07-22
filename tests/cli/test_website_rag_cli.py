from hermes_agent.cli.website_rag import build_parser


def test_website_rag_parser_reads_required_arguments() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--url",
            "https://example.com",
            "--question",
            "이 사이트는 무엇인가요?",
        ],
    )

    assert args.url == "https://example.com"
    assert args.question == "이 사이트는 무엇인가요?"
    assert args.generator_model == "qwen3:8b"
    assert args.embedding_model == "nomic-embed-text"
    assert args.chunk_size == 500
    assert args.top_k == 3


def test_website_rag_parser_reads_optional_arguments() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--url",
            "https://example.com",
            "--question",
            "서비스는 무엇인가요?",
            "--generator-model",
            "qwen3:8b",
            "--embedding-model",
            "nomic-embed-text",
            "--chunk-size",
            "300",
            "--top-k",
            "5",
        ],
    )

    assert args.chunk_size == 300
    assert args.top_k == 5
