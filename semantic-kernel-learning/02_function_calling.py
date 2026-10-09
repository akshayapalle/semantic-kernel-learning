
import asyncio
import os
from dotenv import load_dotenv

from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

load_dotenv()


class CalculatorPlugin:
    @kernel_function(
        name="add",
        description="Adds two numbers together",
    )
    def add(self, a: int, b: int) -> int:
        return a + b


async def main():
    kernel = Kernel()

    kernel.add_service(
        AzureChatCompletion(
            deployment_name=os.getenv("AOAI_CHAT_DEPLOYMENT"),
            api_key=os.getenv("AOAI_CHAT_KEY"),
            endpoint=os.getenv("AOAI_CHAT_ENDPOINT"),
            api_version=os.getenv("AOAI_API_VERSION_GPT"),
        )
    )

    kernel.add_plugin(CalculatorPlugin(), plugin_name="Calculator")

    settings = AzureChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    history = ChatHistory()
    history.add_user_message("What is 2 plus 3? Use the calculator.")

    result = await kernel.get_service(
        type=AzureChatCompletion
    ).get_chat_message_contents(
        chat_history=history,
        settings=settings,
        kernel=kernel,
        arguments=KernelArguments(),
    )

    print(result[0])


if __name__ == "__main__":
    asyncio.run(main())