
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


class LightsPlugin:
    lights = [
        {"id": 1, "name": "Table Lamp", "is_on": False},
        {"id": 2, "name": "Porch light", "is_on": False},
        {"id": 3, "name": "Chandelier", "is_on": True},
    ]

    @kernel_function(name="get_lights", description="Gets all lights and their current states")
    def get_lights(self) -> str:
        return str(self.lights)

    @kernel_function(name="change_state", description="Changes a light's state using its ID and the desired on/off state")
    def change_state(self, id: int, is_on: bool) -> str:
        for light in self.lights:
            if light["id"] == id:
                light["is_on"] = is_on
                return f'{light["name"]} is now {"on" if is_on else "off"}.'
        return f"No light found with ID {id}."


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

    kernel.add_plugin(LightsPlugin(), plugin_name="Lights")

    settings = AzureChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    history = ChatHistory()
    history.add_user_message(
        "Turn off the chandelier, then tell me its new state."
    )

    result = await kernel.get_service(type=AzureChatCompletion).get_chat_message_contents(
        chat_history=history,
        settings=settings,
        kernel=kernel,
        arguments=KernelArguments(),
    )

    print("AI response:", result[0])

    # Verify the actual Python plugin state
    lights_result = await kernel.plugins["Lights"]["get_lights"].invoke(kernel)
    print("Verified lights:", lights_result)

if __name__ == "__main__":
    asyncio.run(main())