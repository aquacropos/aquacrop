import sys

if not "-m" in sys.argv:
    from .prepare_weather import prepare_weather
    from .data import get_filepath
    from .lars import prepare_lars_weather, select_lars_wdf
