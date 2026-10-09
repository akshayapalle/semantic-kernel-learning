
def collect_task():
    print("Step 1: Collecting task")
    return "Build a login page"


def process_task(task):
    print("Step 2: Processing task")
    return f"Processed: {task}"


def review_task(result):
    print("Step 3: Reviewing task")
    return f"Review complete — {result}"


# Sequential workflow
task = collect_task()
processed = process_task(task)
final_result = review_task(processed)

print("\nFinal result:", final_result)