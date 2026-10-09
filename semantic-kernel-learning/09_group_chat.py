
import asyncio
import os
from dotenv import load_dotenv

from semantic_kernel.agents import ChatCompletionAgent
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
        "You are a researcher. Identify the important points "
        "about the given topic. Keep your answer concise."
    ),
    description="Researches the topic and identifies important points.",
    service=create_service(),
)


writer = ChatCompletionAgent(
    name="WriterAgent",
    instructions=(
        "You are a technical writer. Turn the provided research "
        "points into a clear, beginner-friendly explanation."
    ),
    description="Writes a beginner-friendly explanation using research findings.",
    service=create_service(),
)

reviewer = ChatCompletionAgent(
    name="ReviewerAgent",
    instructions=(
        "You are a reviewer. Check the provided explanation for "
        "clarity, correctness, and missing important points. "
        "Give concise feedback."
    ),
    description="Reviews the explanation for clarity, correctness, and missing points.",
    service=create_service(),
)


async def main():
    from semantic_kernel.agents import (
        GroupChatOrchestration,
        RoundRobinGroupChatManager,
    )
    from semantic_kernel.agents.runtime import InProcessRuntime

    async def response_callback(message):
        print(f"\nAgent response:\n{message}")

    # Create the group and define the speaking order
    group_chat = GroupChatOrchestration(
        members=[researcher, writer, reviewer],
        manager=RoundRobinGroupChatManager(max_rounds=3),
        agent_response_callback=response_callback,
    )

    # Start the runtime that executes the agents
    runtime = InProcessRuntime()
    runtime.start()

    try:
        result = await group_chat.invoke(
            task="Explain why Python is useful for AI development.",
            runtime=runtime,
        )

        final_result = await result.get()
        print("\nFinal result:")
        print(final_result)
    finally:
        await runtime.stop_when_idle()


if __name__ == "__main__":
    asyncio.run(main())