import asyncio
import os
from dotenv import load_dotenv

from semantic_kernel.agents import (
    ChatCompletionAgent,
    ConcurrentOrchestration,
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
        "You are a researcher. Identify important points "
        "about the given topic. Keep your answer concise."
    ),
    description="Researches the topic and identifies important points.",
    service=create_service(),
)

writer = ChatCompletionAgent(
    name="WriterAgent",
    instructions=(
        "You are a technical writer. Independently create a clear, "
        "beginner-friendly explanation of the given topic."
    ),
    description="Writes a beginner-friendly explanation.",
    service=create_service(),
)

reviewer = ChatCompletionAgent(
    name="ReviewerAgent",
    instructions=(
        "You are a reviewer. Independently explain what makes an "
        "answer about the given topic clear, correct, and complete. "
        "Keep your response concise."
    ),
    description="Provides an independent review perspective.",
    service=create_service(),
)


async def main():
    orchestration = ConcurrentOrchestration(
        members=[researcher, writer, reviewer],
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

        if isinstance(final_result, list):
            for item in final_result:
                print(item)
        else:
            print(getattr(final_result))

    finally:
        await runtime.stop_when_idle()


if __name__ == "__main__":
    asyncio.run(main())

