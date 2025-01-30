import time
from typing import Dict
import random

class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        self.user_last_message_time: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        last_time = self.user_last_message_time.get(user_id)
        if last_time is None:
            return True
        return (time.time() - last_time) >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            self.user_last_message_time[user_id] = time.time()
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        last_time = self.user_last_message_time.get(user_id)
        if last_time is None:
            return 0.0
        elapsed_time = time.time() - last_time
        return max(0.0, self.min_interval - elapsed_time)

def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)
    test_users = [str(i) for i in range(1, 6)]

    print("\n=== Симуляція потоку повідомлень (Throttling) ===")
    for message_id in range(1, 11):
        user_id = random.choice(test_users)
        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = random.choice(test_users)
        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_throttling_limiter()
