import uuid

import pytest

from temporalio import activity
from temporalio.worker import Worker
from temporalio.testing import WorkflowEnvironment

from activities import find_prime
from workflows.prime_workflow import FindPrimeFlow

@pytest.mark.asyncio
async def test_execute_prime_workflow():
    task_queue_name = str(uuid.uuid4())
    async with await WorkflowEnvironment.start_time_skipping() as env:

        async with Worker(
            env.client,
            task_queue=task_queue_name,
            workflows=[FindPrimeFlow],
            activities=[find_prime],
        ):
            assert 11 == await env.client.execute_workflow(
                FindPrimeFlow.run,
                5,
                id=str(uuid.uuid4()),
                task_queue=task_queue_name,
            )

@activity.defn(name="find_prime")
async def find_prime_mocked(n: int) -> int:
    if (n == 4):
        return 7
    if (n == 5):
        return 11
    if (n == 10):
        return 29
    if (n == 100):
        return 541

@pytest.mark.asyncio
async def test_find_prime_mocked():
    test_input = { 5: 11, 10: 29, 100: 541}
    task_queue_name = str(uuid.uuid4())
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue=task_queue_name,
            workflows=[FindPrimeFlow],
            activities=[find_prime_mocked],
        ):
            for n, expected in test_input.items():
                print(f"\nTesting {n} -> {expected}")
                assert expected == await env.client.execute_workflow(
                    FindPrimeFlow.run,
                    n,
                    id=str(uuid.uuid4()),
                    task_queue=task_queue_name,
                )