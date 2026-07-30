from slowapi import Limiter
from slowapi.util import get_remote_address

# In-memory limiter: sufficient for a single-instance MVP deployment (PRD §7.7 — one
# household, no need for a distributed store like Redis at this scale).
limiter = Limiter(key_func=get_remote_address)
