from rest_framework.throttling import AnonRateThrottle

class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'  # Matches the key in DEFAULT_THROTTLE_RATES
