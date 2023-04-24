import uuid

import pytest

from temporalio.worker import Worker
from temporalio.testing import WorkflowEnvironment

from workflows.prime_factorial_workflow import PrimeFactorialFlow

from tests.test_factorial_workflow import find_factorial_mocked
from tests.test_prime_workflow import find_prime_mocked

from activities import find_factorial_activity, find_prime

@pytest.mark.asyncio
async def test_find_prime_factorial_flow():
    test_input = { 4: 5040, 5: 39916800, 10: 8841761993739701954543616000000}
    task_queue_name = str(uuid.uuid4())
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue=task_queue_name,
            workflows=[PrimeFactorialFlow],
            activities=[find_factorial_activity, find_prime],
        ):
            for n, expected in test_input.items():
                print(f"\nTesting {n} -> {expected}")
                assert expected == await env.client.execute_workflow(
                    PrimeFactorialFlow.run,
                    n,
                    id=str(uuid.uuid4()),
                    task_queue=task_queue_name,
                )

@pytest.mark.asyncio
async def test_find_prime_factorial_flow_mocked():
    test_input = { 4: 5040, 5: 39916800, 10: 8841761993739701954543616000000}
    task_queue_name = str(uuid.uuid4())
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue=task_queue_name,
            workflows=[PrimeFactorialFlow],
            activities=[find_factorial_mocked, find_prime_mocked],
        ):
            for n, expected in test_input.items():
                print(f"\nTesting {n} -> {expected}")
                assert expected == await env.client.execute_workflow(
                    PrimeFactorialFlow.run,
                    n,
                    id=str(uuid.uuid4()),
                    task_queue=task_queue_name,
                )