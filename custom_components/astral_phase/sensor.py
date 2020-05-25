"""
Support for functionality to track the phase of the day.
"""
import asyncio
import logging

import voluptuous as vol

from homeassistant.components.sensor import ENTITY_ID_FORMAT, PLATFORM_SCHEMA
from homeassistant.const import (ATTR_ENTITY_ID, ATTR_ICON, STATE_UNKNOWN)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity, async_generate_entity_id
from homeassistant.helpers.sun import get_astral_location

from .astral_helper import (PHASE_UNKNOWN, PHASE_DAWN, PHASE_SUNRISE,
    PHASE_MORNING, PHASE_DAY, PHASE_EVENING, PHASE_SUNSET, PHASE_TWILIGHT,
    PHASE_NIGHT, TRANSITION_ELEVATION, get_astral_phase)

DEPENDENCIES = ['sun']

_LOGGER = logging.getLogger(__name__)

ENTITY_ID = 'astral_phase'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional('transition_phase', default=True): cv.boolean,
    vol.Optional('transition_elevation',
        default=TRANSITION_ELEVATION): vol.Coerce(float),
})

ATTR_ELEVATION = 'elevation'

PHASE_UNKNOWN_ICON = "mdi:help"
PHASE_DAWN_ICON = "mdi:weather-sunset-up"
PHASE_SUNRISE_ICON = "mdi:weather-sunset-up"
PHASE_MORNING_ICON = "mdi:weather-sunset"
PHASE_DAY_ICON = "mdi:weather-sunny"
PHASE_EVENING_ICON = "mdi:weather-sunset"
PHASE_SUNSET_ICON = "mdi:weather-sunset-up"
PHASE_TWILIGHT_ICON = "mdi:weather-sunset-up"
PHASE_NIGHT_ICON = "mdi:weather-night"

PHASE_ICONS = {
    PHASE_UNKNOWN: PHASE_UNKNOWN_ICON,
    PHASE_DAWN: PHASE_DAWN_ICON,
    PHASE_SUNRISE: PHASE_SUNRISE_ICON,
    PHASE_MORNING: PHASE_MORNING_ICON,
    PHASE_DAY: PHASE_DAY_ICON,
    PHASE_EVENING: PHASE_EVENING_ICON,
    PHASE_SUNSET: PHASE_SUNSET_ICON,
    PHASE_TWILIGHT: PHASE_TWILIGHT_ICON,
    PHASE_NIGHT: PHASE_NIGHT_ICON
}

@asyncio.coroutine
# pylint: disable=unused-argument
def async_setup_platform(hass, config, async_add_devices,
     discovery_info=None):
    """Setup the sensor platform."""

    sensor = AstralPhaseSensor(hass, config)

    async_add_devices([sensor])    
    return True

class AstralPhaseSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass, config):
        """Initialize the sensor."""
        self.hass = hass
        self._config = config
        self._use_transition = config.get('transition_phase')
        self._transition_elevation = config.get('transition_elevation')
        
        if self._use_transition:
            _LOGGER.debug("Using transition phase with %f" % (
                self._transition_elevation))
        else:
            _LOGGER.debug("Transition phase disabled.")
        
        self.entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, ENTITY_ID,
                                                  hass=hass)

        self._attributes = {}
        self._state = PHASE_UNKNOWN
        self._icon = PHASE_ICONS[PHASE_UNKNOWN]

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Astral Phase'

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._attributes

    @asyncio.coroutine
    def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        use_transition = self._use_transition
        transition_elevation = self._transition_elevation
        location = get_astral_location(self.hass)

        # Using local states for async method. Must sync before return.
        state = PHASE_UNKNOWN

        elevation = location.solar_elevation()
        _LOGGER.debug("Current elevation: %r" % elevation)

        attributes = self._attributes or {}
        attributes[ATTR_ELEVATION] = elevation

        state = get_astral_phase(location, use_transition=use_transition, transition_elevation=transition_elevation)
        
        self._state = state
        self._icon = PHASE_ICONS[state]
        self._attributes = attributes
        _LOGGER.debug("Updated astral_phase: %s, %f" %
             (state, elevation))
