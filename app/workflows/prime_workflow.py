from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import find_prime
    from datetime import timedelta

@workflow.defn
class FindPrimeFlow:
    @workflow.run
    async def run(self, n: int) -> int:
        result = await workflow.execute_activity(
            find_prime, n, start_to_close_timeout=timedelta(seconds=5)
        )

        return result