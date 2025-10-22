"""
Configuration for Kurdish corpus expansion
"""

# Scraper configurations
SCRAPER_CONFIGS = {
    'kurdsat': {
        'enabled': True,
        'political': {'clicks': 30},  # Re-enabled with proper button click fix
        'specialized': {'articles_per_category': 20},  # Re-enabled
        'categories': ['Health', 'Science', 'Technology']
    },
    'rudaw': {
        'enabled': True,  # FIXED - using .content div selector with sentence splitting
        'political': {'scrolls': 20},
        'specialized': {'scrolls_per_category': 10},
        'categories': ['Economy', 'Health', 'Sport', 'Culture', 'Interview']
    },
    'khak': {
        'enabled': True,
        'political': {'pages': 10},
        'specialized': None
    },
    'nrt': {
        'enabled': True,
        'political': {'clicks': 15},
        'specialized': {'clicks': 10},
        'categories': ['Economy', 'Social', 'Culture', 'Science', 'Technology']
    },
    'awene': {
        'enabled': True,
        'political': {'pages': 10},
        'specialized': {'articles_per_category': 30},
        'categories': ['Articles', 'Culture', 'Economy', 'Health', 'Multimedia']
    },
    'kurdistan24': {
        'enabled': True,
        'political': {'pages': 10},
        'specialized': {'pages_per_category': 5},
        'categories': ['Economy', 'Culture', 'Artistic', 'Social', 'Health', 'Science-Technology'],
        'requires_flaresolverr': True
    },
    'xendan': {
        'enabled': True,
        'political': {'pages': 10},
        'specialized': {'pages_per_category': 5},
        'categories': ['Sport', 'Economy', 'Technology']
    },
    'sekokurd': {
        'enabled': True,
        'political': None,
        'specialized': {'clicks': 10},
        'categories': ['Articles', 'Culture']
    },
    'govkrd': {
        'enabled': True,
        'political': {'pages': 10},
        'specialized': None
    },
    'sharpress': {
        'enabled': True,
        'political': {'pages': 10},
        'specialized': {'pages': 5},
        'categories': ['Economy', 'Sport', 'Culture', 'Health', 'Opinion', 'Research and Analysis']
    },
    'lvinpress': {
        'enabled': True,
        'political': {'pages': 10},
        'specialized': {'pages': 5},
        'categories': ['Social Media', 'Opinion']
    },
    'balinde': {
        'enabled': True,
        'political': None,  # No political content - poetry/literature site
        'specialized': {'pages': 10},
        'categories': ['Kurdish Poetry', 'Articles']
    }
}

# Quality control settings
QC_SETTINGS = {
    'min_words': 10,
    'max_words': 30,
    'min_kurdish_ratio': 0.7
}

# Output settings
OUTPUT_FILE = 'corpus/kurdish_expanded_batch3.txt'

# FlareSolverr settings
FLARESOLVERR_URL = 'http://localhost:8191'
FLARESOLVERR_TIMEOUT = 90

# General settings
HEADLESS = True
PAGE_LOAD_TIMEOUT = 30
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_DELAY = 2
