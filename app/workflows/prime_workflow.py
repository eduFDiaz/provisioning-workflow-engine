from datetime import timedelta
from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import find_prime

@workflow.defn
class FindPrimeFlow:
    @workflow.run
    async def run(self, prime: int) -> str:
        return await workflow.execute_activity(
            find_prime, prime, start_to_close_timeout=timedelta(seconds=5)
        )