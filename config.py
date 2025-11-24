# GraphHopper API Configuration
GRAPHHOPPER_API_URL = "http://localhost:8989/route"
GRAPHHOPPER_PROFILE = "foot"  # Use "foot" for pedestrian routing

# Default coordinates (Bangalore, India)
DEFAULT_START_LAT = 12.9716
DEFAULT_START_LON = 77.5946
DEFAULT_END_LAT = 12.9352
DEFAULT_END_LON = 77.6245

# Pedestrian-specific settings
WALKING_SPEED_KMH = 5.0  # Average walking speed in km/h
MAX_WALKING_DISTANCE_KM = 10.0  # Maximum reasonable walking distance

# API Request Parameters
ROUTE_PARAMS = {
    'profile': GRAPHHOPPER_PROFILE,
    'points_encoded': 'false',
    'elevation': 'false',
    'instructions': 'true',
    'calc_points': 'true',
    'details': 'street_name,distance,time'
}

# Pedestrian-specific features to consider
PEDESTRIAN_PREFERENCES = {
    'prefer_footways': True,
    'avoid_highways': True,
    'prefer_sidewalks': True,
    'avoid_stairs': False,  # Set to True if user cannot use stairs
    'max_slope': 10.0  # Maximum slope percentage
}

# Safety settings
SAFETY_SETTINGS = {
    'avoid_dark_alleys': True,
    'prefer_well_lit_areas': True,
    'avoid_construction': True
}

# Audio guidance settings (for blind navigation)
AUDIO_GUIDANCE = {
    'instruction_interval': 50,  # meters
    'turn_warning_distance': 20,  # meters before turn
    'hazard_warning_distance': 10,  # meters before hazard
    'announce_landmarks': True,
    'announce_street_names': True
}

# Error handling
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = "pedestrian_navigation.log"

# Map bounds (optional - for validation)
MAP_BOUNDS = {
    'min_lat': 12.0,
    'max_lat': 13.5,
    'min_lon': 77.0,
    'max_lon': 78.5
}