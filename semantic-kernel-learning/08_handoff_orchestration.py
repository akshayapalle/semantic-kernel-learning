
import asyncio
import os
from dotenv import load_dotenv

from semantic_kernel.agents import (
    ChatCompletionAgent,
    HandoffOrchestration,
    OrchestrationHandoffs,
)
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

load_dotenv()


def create_service():
    return AzureChatCompletion(
        deployment_name=os.getenv("AOAI_CHAT_DEPLOYMENT"),
        endpoint=os.getenv("AOAI_CHAT_ENDPOINT"),
        api_key=os.getenv("AOAI_CHAT_KEY"),
        api_version=os.getenv("AOAI_API_VERSION_GPT"),
    )


def response_callback(message):
    print(f"\n{message.name}: {message.content}")


async def main():
    # Agent 1: Routes the request
    triage_agent = ChatCompletionAgent(
        name="TriageAgent",
        description="Routes software development questions to the right specialist.",
        instructions=(
            "You are a triage agent. "
            "For backend or authentication questions, you MUST call "
            "transfer_to_BackendAgent. Do not answer these questions yourself."
        ),
        function_choice_behavior=FunctionChoiceBehavior.Auto(),
        service=create_service(),
    )

    # Agent 2: Handles backend questions
    backend_agent = ChatCompletionAgent(
        name="BackendAgent",
        description="Specializes in backend APIs and authentication.",
        instructions=(
            "You are a backend specialist. "
            "Answer backend and authentication questions clearly. "
            "After providing your answer, call complete_task with a brief summary."
        ),
        function_choice_behavior=FunctionChoiceBehavior.Auto(),
        service=create_service(),
    )

    # Define who can hand off to whom
    handoffs = (
        OrchestrationHandoffs()
        .add(
            source_agent="TriageAgent",
            target_agent="BackendAgent",
            description="Transfer backend and authentication questions to BackendAgent.",
        )
    )

    # Create the handoff orchestration
    orchestration = HandoffOrchestration(
        members=[triage_agent, backend_agent],
        handoffs=handoffs,
        agent_response_callback=response_callback,
    )

    # Start the runtime
    runtime = InProcessRuntime()
    runtime.start()

    try:
        result = await orchestration.invoke(
            task="Explain the backend steps needed to implement login authentication.",
            runtime=runtime,
        )

        answer = await result.get()
        print("\nFinal result:\n", answer)

    finally:
        await runtime.stop_when_idle()


if __name__ == "__main__":
    asyncio.run(main())