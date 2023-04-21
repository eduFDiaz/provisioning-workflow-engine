import time
from temporalio import activity

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

def find_nth_prime(n):
    if n == 1:
        return 2
    count = 1
    num = 3
    while count < n:
        if is_prime(num):
            count += 1
        num += 2
    return num - 2

def find_factorial(n):
    # iterative approach
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

@activity.defn
async def find_factorial_activity(n: int) -> int:
    return find_factorial(n)

@activity.defn
async def find_prime(n: int) -> int:
    return find_nth_prime(n)