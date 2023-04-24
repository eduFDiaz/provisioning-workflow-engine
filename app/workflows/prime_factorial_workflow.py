
from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import find_prime, find_factorial_activity
    from datetime import timedelta
    from config import logger as log

@workflow.defn
class PrimeFactorialFlow:
    @workflow.run
    async def run(self, n: int) -> int:

        result1 = await workflow.execute_activity(
            find_prime, n, start_to_close_timeout=timedelta(seconds=5)
        )
        log.info(f"find_prime: {n}! = {result1}")

        result = await workflow.execute_activity(
            find_factorial_activity, result1, start_to_close_timeout=timedelta(seconds=5)
        )
        log.info(f"find_factorial_activity: {n}! = {result}")

        return result