import os
import time
from collections import deque
from groq import Groq, RateLimitError
from src.config import LLM_MODEL, LLM_TEMPERATURE, MAX_TOKENS_RESPONSE

class RateLimiter:
    def __init__(self, rpm=30, tpm=8000, rpd=1000, tpd=200000):
        self.rpm = rpm
        self.tpm = tpm
        self.rpd = rpd
        self.tpd = tpd
        self.minute_history = deque()
        self.day_history = deque()

    def _cleanup(self):
        now = time.time()
        while self.minute_history and now - self.minute_history[0][0] > 60:
            self.minute_history.popleft()
        while self.day_history and now - self.day_history[0][0] > 86400:
            self.day_history.popleft()

    def check_capacity(self, estimated_tokens: int) -> bool:
        self._cleanup()
        reqs_min = len(self.minute_history)
        tokens_min = sum(t for _, t in self.minute_history)
        reqs_day = len(self.day_history)
        tokens_day = sum(t for _, t in self.day_history)
        
        if reqs_day >= self.rpd or (tokens_day + estimated_tokens) > self.tpd:
            raise RuntimeError("Daily LLM rate limit exceeded (1K RPM or 200K TPD).")
            
        if reqs_min < self.rpm and (tokens_min + estimated_tokens) <= self.tpm:
            return True
        return False

    def wait_for_capacity(self, estimated_tokens: int):
        first_wait = True
        while not self.check_capacity(estimated_tokens):
            if first_wait:
                print("\n[Rate Limiter] Approaching limits. Waiting for capacity to reset...", end="", flush=True)
                first_wait = False
            time.sleep(2)
        if not first_wait:
            print(" Resuming.", flush=True)

    def add_usage(self, tokens: int):
        now = time.time()
        self.minute_history.append((now, tokens))
        self.day_history.append((now, tokens))

class AnswerGenerator:
    def __init__(self):
        self.client = Groq()
        # openai/gpt-oss-120b limits
        self.rate_limiter = RateLimiter(rpm=30, tpm=8000, rpd=1000, tpd=200000)
        
    def generate(self, prompt: str) -> str:
        # Roughly estimate prompt tokens + max generation tokens
        estimated_prompt_tokens = len(prompt) // 4
        estimated_total_tokens = estimated_prompt_tokens + MAX_TOKENS_RESPONSE
        
        try:
            self.rate_limiter.wait_for_capacity(estimated_total_tokens)
        except RuntimeError as e:
            return str(e)
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=LLM_TEMPERATURE,
                    max_tokens=MAX_TOKENS_RESPONSE,
                )
                
                actual_tokens = response.usage.total_tokens if response.usage else estimated_total_tokens
                self.rate_limiter.add_usage(actual_tokens)
                
                return response.choices[0].message.content
                
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    return f"I'm currently experiencing high traffic and hit an API rate limit. Please try again later. (Error: {str(e)})"
                time.sleep(5 * (attempt + 1))  # Exponential backoff
            except Exception as e:
                return f"An error occurred during generation: {str(e)}"
