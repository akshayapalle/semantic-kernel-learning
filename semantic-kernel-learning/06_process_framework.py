
import asyncio
import os
from dotenv import load_dotenv

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import kernel_function, KernelArguments
from semantic_kernel.processes import ProcessBuilder
from semantic_kernel.processes.kernel_process import (
    KernelProcessStep,
    KernelProcessEvent,
)
from semantic_kernel.processes.local_runtime.local_kernel_process import start

load_dotenv()


class CollectTaskStep(KernelProcessStep):
    @kernel_function
    def collect_task(self, task: str) -> str:
        print("Step 1: Collecting task")
        return task


class AIPlannerStep(KernelProcessStep):
    @kernel_function
    async def plan_task(self, kernel: Kernel, task: str) -> str:
        print("Step 2: Asking Azure OpenAI to plan the task")

        prompt = """
        You are a software project planner.

        Create a simple, numbered implementation plan for this task:
        {{$task}}
        """

        result = await kernel.invoke_prompt(
            prompt,
            arguments=KernelArguments(task=task),
        )

        plan = str(result)
        print("\nAI-generated plan:\n", plan)
        return plan


async def main():
    # Configure Azure OpenAI
    kernel = Kernel()

    kernel.add_service(
        AzureChatCompletion(
            deployment_name=os.getenv("AOAI_CHAT_DEPLOYMENT"),
            endpoint=os.getenv("AOAI_CHAT_ENDPOINT"),
            api_key=os.getenv("AOAI_CHAT_KEY"),
            api_version=os.getenv("AOAI_API_VERSION_GPT"),
        )
    )

    # Create the process
    builder = ProcessBuilder(name="AITaskWorkflow")

    collect_step = builder.add_step(CollectTaskStep)
    planner_step = builder.add_step(AIPlannerStep)

    # Connect the steps
    builder.on_input_event("Start").send_event_to(
        target=collect_step
    )

    collect_step.on_function_result(
        function_name="collect_task"
    ).send_event_to(
        target=planner_step,
        function_name="plan_task",
        parameter_name="task",
    )

    process = builder.build()

    # Run the process
    async with await start(
        process=process,
        kernel=kernel,
        initial_event=KernelProcessEvent(
            id="Start",
            data="Build a login page",
        ),
    ) as context:
        await context.get_state()


if __name__ == "__main__":
    asyncio.run(main())