import asyncio
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function


class CalculatorPlugin:
    @kernel_function(name="add", description="Adds two numbers")
    def add(self, a: int, b: int) -> int:
        return a + b


async def main():
    kernel = Kernel()

    kernel.add_plugin(CalculatorPlugin(), plugin_name="Calculator")
    print("Plugin added successfully!")

    calculator = kernel.plugins["Calculator"]
    result = await calculator["add"].invoke(kernel, a=2, b=3)

    print("Result:", result)


if __name__ == "__main__":
    asyncio.run(main())