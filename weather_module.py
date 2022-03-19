#!/usr/bin/python
import logging
import json
import sys
if (sys.version_info > (3,0)):
    import urllib.request
else:
    import urllib
import requests # conda install requests or pip install requests
from settings import LATITUDE, LONGITUDE


logger = logging.getLogger('app')

# Global variables.
forecast_url = None


def get_forecast_URL_from_lat_long(latitude: int, longitude: int):
    """
    Make a request to api.weather.gov specifying latitude and longitude.
    The response should give us, among other things, the URL for the local weather forecast.
    """
    # Param check.
    if (latitude is None) or (longitude is None):
        logger.warning('weather_module.get_forecast_URL_from_lat_long(); missing latitude or longitude.')
        return None

    logger.info('weather_module.get_forecast_URL_from_lat_long(); trying...')
    api_url_base = 'https://api.weather.gov'
    current_obs_url = '{0}/points/{1},{2}'.format(api_url_base, latitude, longitude)
    response = requests.get(current_obs_url)
    if response.status_code == 200:
        forecast_data = json.loads(response.content.decode('utf-8'))
        if forecast_data['properties']['forecast']:
            logger.info('weather_module.get_forecast_URL_from_lat_long(); returning forecast URL.')
            return forecast_data['properties']['forecast']
        else:
            logger.warning('weather_module.get_forecast_URL_from_lat_long(); no URL to return.')
            return None
    else:
        logger.warning('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
        return None


def get_weather_forecast_from_URL(forecast_URL: str):
    """
    Make a request to api.weather.gov using a URL that should return local the weather forecast.
    We trim down the response and return only the list of 'periods' for the weather forecast.
    The 'periods' seem to be in pairs corresponding to day and night forecasts for the coming days.
    """

    # Param check.
    if forecast_URL is None:
        logger.warning('weather_module.get_weather_forecast_from_URL(); missing URL.')
        return None

    logger.info("weather_module.get_weather_forecast_from_URL(); trying....")
    response = requests.get(forecast_URL)
    if response.status_code == 200:
        forecast_data = json.loads(response.content.decode('utf-8'))
        if forecast_data['properties']['periods']:
            logger.info("weather_module.get_weather_forecast_from_URL(); got forecast data.")
            return forecast_data['properties']['periods']
        else:
            logger.info("weather_module.get_weather_forecast_from_URL(); no data to return.")
            return None
    else:
        logger.warning('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
        return None


def get_weather_forecast():
    """
    Calls above functions to get a list of 'period' weather forecast data from api.weather.gov.
    LATITUDE and LONGITUDE are expected to be present in a settings.py file.
    """

    global forecast_url

    # Get the forecast URL from latitude and longitude.
    if forecast_url is None:
        forecast_url = get_forecast_URL_from_lat_long(LATITUDE, LONGITUDE)
    
    # Get current forecast periods.
    return get_weather_forecast_from_URL(forecast_url)

