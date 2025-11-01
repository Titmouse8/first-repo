from rest_framework.throttling import UserRateThrottle

# BurstThrottle urcime kolko requests môze uzivatel poslat v kratkom case
# SustainedThrottle urcime kolko requests môze uzivatel poslat v dlhsom casovom obdodi
class BurstThrottle(UserRateThrottle):
    scope='burst'

class SustainedThrottle(UserRateThrottle):
    scope='sustained'