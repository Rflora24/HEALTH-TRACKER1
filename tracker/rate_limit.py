from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

class RateLimiter:
    """Rate limiting utility for API endpoints."""
    
    def __init__(self, key_prefix='rl_', cache_timeout=300):
        """
        Initialize the rate limiter.
        
        Args:
            key_prefix: Prefix for cache keys
            cache_timeout: Cache timeout in seconds
        """
        self.key_prefix = key_prefix
        self.cache_timeout = cache_timeout
        self.logger = logging.getLogger('tracker.rate_limit')
        
    def generate_key(self, request, endpoint):
        """Generate a unique cache key for the request."""
        return f"{self.key_prefix}{endpoint}_{request.META.get('REMOTE_ADDR')}"
        
    def is_allowed(self, request, endpoint, limit, period):
        """
        Check if the request is allowed based on rate limits.
        
        Args:
            request: Django request object
            endpoint: API endpoint name
            limit: Maximum number of requests allowed
            period: Time period in seconds
            
        Returns:
            tuple: (is_allowed, remaining_time)
        """
        key = self.generate_key(request, endpoint)
        
        # Get current count and timestamp
        data = cache.get(key, {'count': 0, 'timestamp': timezone.now().timestamp()})
        current_count = data['count']
        last_reset = data['timestamp']
        
        # Check if we need to reset the counter
        if timezone.now().timestamp() - last_reset > period:
            current_count = 0
            last_reset = timezone.now().timestamp()
            
        # Check if we've reached the limit
        if current_count >= limit:
            remaining_time = period - (timezone.now().timestamp() - last_reset)
            self.logger.warning(f"Rate limit exceeded for {endpoint} from {request.META.get('REMOTE_ADDR')}"
                              f" - {remaining_time:.0f} seconds remaining")
            return False, remaining_time
            
        # Update count
        current_count += 1
        cache.set(key, 
                  {'count': current_count, 'timestamp': last_reset}, 
                  self.cache_timeout)
        
        return True, 0
        
    def get_remaining_time(self, request, endpoint):
        """Get remaining time until rate limit resets."""
        key = self.generate_key(request, endpoint)
        data = cache.get(key)
        if not data:
            return 0
            
        current_time = timezone.now().timestamp()
        remaining_time = data['timestamp'] + self.cache_timeout - current_time
        return max(0, remaining_time)
