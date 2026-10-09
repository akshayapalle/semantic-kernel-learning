import asyncio
import logging
import os
from dotenv import load_dotenv

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from typing import Annotated
from semantic_kernel.functions import kernel_function

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

load_dotenv()


# Step 6 — Create a native plugin
class LightsPlugin:
    lights = [
        {"id": 1, "name": "Table Lamp", "is_on": False},
        {"id": 2, "name": "Porch light", "is_on": False},
        {"id": 3, "name": "Chandelier", "is_on": True},
    ]

    @kernel_function(
        name="get_lights",
        description="Gets a list of lights and their current state",
    )
    def get_state(
        self,
    ) -> str:
        """Gets a list of lights and their current state."""
        return self.lights

    @kernel_function(
        name="change_state",
        description="Changes the state of the light",
    )
    def change_state(
        self,
        id: int,
        is_on: bool,
    ) -> str:
        """Changes the state of the light."""
        for light in self.lights:
            if light["id"] == id:
                light["is_on"] = is_on
                return light
        return None

    
# 2) Add AI services


async def main():
    # Initialize the kernel
    kernel = Kernel()

    print("Endpoint:", os.getenv("AOAI_CHAT_ENDPOINT"))
    print("Deployment:", os.getenv("AOAI_CHAT_DEPLOYMENT"))

    # Add Azure OpenAI chat completion
    kernel.add_service(AzureChatCompletion(
    deployment_name=os.getenv("AOAI_CHAT_DEPLOYMENT"),
    api_key=os.getenv("AOAI_CHAT_KEY"),
    endpoint=os.getenv("AOAI_CHAT_ENDPOINT"),
    api_version=os.getenv("AOAI_API_VERSION_GPT"),
))

    # Step 3 — Add enterprise services
    logging.basicConfig(
        format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("kernel").setLevel(logging.DEBUG)

    # Step 4 — Retrieve the chat completion service
    chat_completion: AzureChatCompletion = kernel.get_service(
        type=ChatCompletionClientBase
    )

    # Add the plugin to the kernel
    kernel.add_plugin(
    LightsPlugin(),
    plugin_name="Lights",
    )

    # Enable planning
    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    history = ChatHistory()

    history.add_user_message("What lights are available?")

    result = (await chat_completion.get_chat_message_contents(
    chat_history=history,
    settings=execution_settings,
    kernel=kernel,
    arguments=KernelArguments(),
    ))[0]
 
    print(result)

if __name__ == "__main__":
    asyncio.run(main())


















# import os
# from semantic_kernel.contents import ChatHistory
# from dotenv import load_dotenv

# from semantic_kernel import Kernel
# from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

# load_dotenv()

# kernel = Kernel()

# chat_completion = AzureChatCompletion(
#     deployment_name = os.getenv("AOAI_CHAT_DEPLOYMENT"),
#     endpoint = os.getenv("AOAI_CHAT_ENDPOINT"),
#     api_key=os.getenv("AOAI_CHAT_KEY"),
#     api_version=os.getenv("AOAI_API_VERSION_GPT")
# )

# kernel.add_service(chat_completion) # Kernel + Azure OpenAI connection is set up. # Kernel, here is the AI service you should use

# print("Kernel created successfully!")

