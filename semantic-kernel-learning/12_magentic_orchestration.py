import asyncio
import os
from dotenv import load_dotenv

from semantic_kernel.agents import (
    ChatCompletionAgent,
    MagenticOrchestration,
    StandardMagenticManager,
)
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

load_dotenv()


def create_service():
    return AzureChatCompletion(
        deployment_name=os.getenv("AOAI_CHAT_DEPLOYMENT"),
        endpoint=os.getenv("AOAI_CHAT_ENDPOINT"),
        api_key=os.getenv("AOAI_CHAT_KEY"),
        api_version=os.getenv("AOAI_API_VERSION_GPT"),
    )


researcher = ChatCompletionAgent(
    name="ResearcherAgent",
    instructions=(
        "Research the topic and identify important facts. "
        "Keep your response concise."
    ),
    description="Researches topics and identifies important facts.",
    service=create_service(),
)

writer = ChatCompletionAgent(
    name="WriterAgent",
    instructions=(
        "Write a clear, beginner-friendly explanation "
        "of the given topic."
    ),
    description="Writes clear, beginner-friendly explanations.",
    service=create_service(),
)

reviewer = ChatCompletionAgent(
    name="ReviewerAgent",
    instructions=(
        "Review the available answer for clarity, correctness, "
        "and missing important points. Suggest improvements."
    ),
    description="Reviews answers for clarity and correctness.",
    service=create_service(),
)


async def main():
    manager = StandardMagenticManager(
        chat_completion_service=create_service(),
        max_iterations=5,
    )

    orchestration = MagenticOrchestration(
        members=[researcher, writer, reviewer],
        manager=manager,
    )

    runtime = InProcessRuntime()
    runtime.start()

    try:
        result = await orchestration.invoke(
            task="Explain why Python is useful for AI development.",
            runtime=runtime,
        )

        final_result = await result.get()

        print("\n--- Final Result ---")
        print(getattr(final_result, "content", final_result))

    finally:
        await runtime.stop_when_idle()


if __name__ == "__main__":
    asyncio.run(main())
