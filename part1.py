import random
import time
from collections import deque
from typing import Dict

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_messages: Dict[str, deque] = {}
    
    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """Видаляє старі записи з черги, які вийшли за межі вікна."""
        if user_id in self.user_messages:
            while self.user_messages[user_id] and self.user_messages[user_id][0] <= current_time - self.window_size:
                self.user_messages[user_id].popleft()

    def can_send_message(self, user_id: str) -> bool:
        """Перевіряє, чи може користувач надіслати повідомлення."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        return len(self.user_messages.get(user_id, [])) < self.max_requests
    
    def record_message(self, user_id: str) -> bool:
        """Записує повідомлення користувача, якщо це дозволено."""
        if self.can_send_message(user_id):
            if user_id not in self.user_messages:
                self.user_messages[user_id] = deque()
            self.user_messages[user_id].append(time.time())
            return True
        return False
    
    def time_until_next_allowed(self, user_id: str) -> float:
        """Розраховує час, що залишився до можливості відправити наступне повідомлення."""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if user_id not in self.user_messages or not self.user_messages[user_id]:
            return 0.0
        return max(0.0, self.window_size - (current_time - self.user_messages[user_id][0]))

# Демонстрація роботи

def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 5)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = str(message_id % 5 + 1)  # Користувачі з ID від 1 до 5

        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = str(message_id % 5 + 1)
        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
