"""Helper for astral_phase"""

import logging
from datetime import datetime

from homeassistant.const import STATE_UNKNOWN

_LOGGER = logging.getLogger(__name__)

# The elevation that demarcates daytime from morning/evening time.
# This is not in any way an official number, but is simply the inverse of the
# astronomical depression value that demarcates dawn/twilight from night.
TRANSITION_ELEVATION = 18

PHASE_UNKNOWN = STATE_UNKNOWN
PHASE_DAWN = "dawn"
PHASE_SUNRISE = "sunrise"
PHASE_MORNING = "morning"
PHASE_DAY = "day"
PHASE_EVENING = "evening"
PHASE_SUNSET = "sunset"
PHASE_TWILIGHT = "twilight"
PHASE_NIGHT = "night"

# location: Astral location
# dt: datetime
def get_sun_rising(location, dt):
    solar_noon = location.solar_noon(date=dt.date())
    sun_rising = dt < solar_noon
    return sun_rising

# location: Astral location
# dt: datetime
def get_astral_phase(location, dt=None, use_transition=True, transition_elevation=TRANSITION_ELEVATION):

    if dt is None:
        dt = datetime.now(tz=location.tz)

    elevation = location.solar_elevation(dt)
    sun_rising = get_sun_rising(location, dt)
    phase = PHASE_UNKNOWN

    # Day and Night do not require the knowledge of the sun's elevation
    # trend.

    if elevation < -location.solar_depression:
        phase = PHASE_NIGHT

    elif elevation >= transition_elevation:
        phase = PHASE_DAY

    else:
        # If the sun's elevation is between the transition point and 0º
        # then we need to know the sun's elevation trend to distinguish
        # dawn from twilight.
        
        if elevation < 0:
            phase = PHASE_DAWN if sun_rising else PHASE_TWILIGHT
        elif elevation < 1:
            phase = PHASE_SUNRISE if sun_rising else PHASE_SUNSET
        elif elevation < transition_elevation and use_transition:
            phase = PHASE_MORNING if sun_rising else PHASE_EVENING
        else:
            # Fail-safe
            phase = PHASE_DAY

    return phase
