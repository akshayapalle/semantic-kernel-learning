
import asyncio
import os
from dotenv import load_dotenv

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import KernelArguments

load_dotenv()


async def main():
    kernel = Kernel()

    kernel.add_service(
        AzureChatCompletion(
            deployment_name=os.getenv("AOAI_CHAT_DEPLOYMENT"),
            endpoint=os.getenv("AOAI_CHAT_ENDPOINT"),
            api_key=os.getenv("AOAI_CHAT_KEY"),
            api_version=os.getenv("AOAI_API_VERSION_GPT"),
        )
    )

    async def create_frontend_plan():
        print("Frontend task started")
        result = await kernel.invoke_prompt(
            "Give a concise 3-step frontend implementation plan for a login page."
        )
        print("Frontend task finished")
        return str(result)

    async def create_backend_plan():
        print("Backend task started")
        result = await kernel.invoke_prompt(
            "Give a concise 3-step backend implementation plan for login authentication."
        )
        print("Backend task finished")
        return str(result)

    # Run both independent tasks concurrently
    frontend_plan, backend_plan = await asyncio.gather(
        create_frontend_plan(),
        create_backend_plan(),
    )

    print("\n--- FRONTEND PLAN ---")
    print(frontend_plan)

    print("\n--- BACKEND PLAN ---")
    print(backend_plan)


if __name__ == "__main__":
    asyncio.run(main())