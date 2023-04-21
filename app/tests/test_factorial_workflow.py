import uuid

import pytest

from temporalio import activity
from temporalio.worker import Worker
from temporalio.testing import WorkflowEnvironment

from activities import find_factorial_activity
from workflows.factorial_workflow import FactorialFlow

@pytest.mark.asyncio
async def test_execute_factorial_workflow():
    task_queue_name = str(uuid.uuid4())
    async with await WorkflowEnvironment.start_time_skipping() as env:

        async with Worker(
            env.client,
            task_queue=task_queue_name,
            workflows=[FactorialFlow],
            activities=[find_factorial_activity],
        ):
            assert 120 == await env.client.execute_workflow(
                FactorialFlow.run,
                5,
                id=str(uuid.uuid4()),
                task_queue=task_queue_name,
            )

# This name should match the real name of the activity in the workflow
# otherwise the workflow will not use the mocked activity
@activity.defn(name="find_factorial_activity")
async def find_factorial_mocked(n: int) -> int:
    if (n == 0):
        return 1
    if (n == 1):
        return 1
    if (n == 5):
        return 120
    if (n == 10):
        return 3628800

@pytest.mark.asyncio
async def test_find_factorial_activity_mocked():
    test_input = { 0: 1, 1: 1, 5: 120, 10: 3628800}
    task_queue_name = str(uuid.uuid4())
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue=task_queue_name,
            workflows=[FactorialFlow],
            activities=[find_factorial_mocked],
        ):
            for n, expected in test_input.items():
                print(f"\nTesting {n} -> {expected}")
                assert expected == await env.client.execute_workflow(
                    FactorialFlow.run,
                    n,
                    id=str(uuid.uuid4()),
                    task_queue=task_queue_name,
                )