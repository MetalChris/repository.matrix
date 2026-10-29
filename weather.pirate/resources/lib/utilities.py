import xbmc

def degToCompass(num):
    val=int((int(num)/22.5)+.5)
    arr=["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    ##print(arr[(val % 16)])
    winddir = arr[(val % 16)]
    return(winddir)

def FEELS_LIKE(T, V=0, R=0):#, ext=''):
    if T <= 10 and V >= 8:
        FeelsLike = WIND_CHILL(T, V)
    elif T >= 26:
        FeelsLike = HEAT_INDEX(T, R)
    else:
        FeelsLike = T * 1.8 + 32
    #if ext == 'F':
        #FeelsLike = FeelsLike * 1.8 + 32
    return (int(round(FeelsLike)))

#### thanks to FrostBox @ http://forum.kodi.tv/showthread.php?tid=114637&pid=937168#pid937168
def WIND_CHILL(T, V):
    FeelsLike = ( 13.12 + ( 0.6215 * T ) - ( 11.37 * V**0.16 ) + ( 0.3965 * T * V**0.16 ) )
    return FeelsLike

### https://en.wikipedia.org/wiki/Heat_index
def HEAT_INDEX(T, R):
    #T = T * 1.8 + 32 # calaculation is done in F
    FeelsLike = -42.379 + (2.04901523 * T) + (10.14333127 * R) + (-0.22475541 * T * R) + (-0.00683783 * T**2) + (-0.05481717 * R**2) + (0.00122874 * T**2 * R) + (0.00085282 * T * R**2) + (-0.00000199 * T**2 * R**2)
    FeelsLike = (FeelsLike - 32) / 1.8 # convert to C
    return FeelsLike

WEATHER_CODES = { 'chanceflurries'    : '41',
                  'chancerain'        : '39',
                  'isorainswrsday'        : '39',
                  'isosleetswrsday'        : '12',
                  'isosleetswrsnight'        : '12',
                  'occlightrain'        : '39',
                  'chancesleet'       : '8',
                  'occlightsleet'       : '8',
                  'chancesnow'        : '41',
                  'chancetstorms'     : '38',
                  'clear-night'             : '31',
                  'cloudy'            : '26',
                  'Overcast night'            : '26',
                  'Overcast'            : '26',
                  'overcast'            : '26',
                  'cloudy skies'            : '26',
                  'flurries'          : '13',
                  'wind'               : '23',
                  'fog'               : '20',
                  'hazy'              : '21',
                  'mostlycloudy'      : '28',
                  'mostlysunny'       : '34',
                  'Partially cloudy'      : '30',
                  'partially cloudy'      : '30',
                  'partcloudrainthunder'      : '30',
                  'partcloudrainthunderday'      : '30',
                  'partcloudrainthundernight'      : '47',
                  'partly-cloudy-day'      : '30',
                  'partly-cloudy-night'      : '33',
                  'partly cloudy night'      : '33',
                  'Partially cloudy night'      : '33',
                  'partially cloudy night'      : '33',
                  'partlysunny'       : '34',
                  'sleet'             : '18',
                  'modsleet'             : '18',
                  'modsleetswrsday'             : '18',
                  'modsleetswrsnight'             : '18',
                  'rain'              : '11',
                  'heavyrainswrsday'              : '11',
                  'heavyrain'              : '11',
                  'freezingrain'              : '11',
                  'freezingdrizzle'              : '7',
                  'modrain'              : '11',
                  'modrainswrsday'              : '11',
                  'modrainswrsnight'              : '11',
                  'heavyrain'              : '11',
                  'mist'              : '11',
                  'light drizzle, mist'              : '11',
                  'light drizzle'              : '11',
                  'light rain shower'              : '11',
                  'showers-day'              : '11',
                  'snow'              : '42',
                  'modsnow'              : '42',
                  'modsnowswrsday'              : '42',
                  'modsnowswrsnight'              : '46',
                  'snow-showers-day'              : '42',
                  'snow-showers-night'              : '46',
                  'cloudsleetsnowthunder'              : '6',
                  'heavysnow'              : '42',
                  'occlightsnow'              : '14',
                  'blizzard'              : '15',
                  'clear-day'             : '32',
                  'sunny skies'             : '32',
                  'cloudrainthunder'           : '38',
                  'thunder-showers-day'           : '38',
                  'thunder-rain'           : '38',
                  'unknown'           : 'na',
                  ''                  : 'na',
                  'nt_chanceflurries' : '46',
                  'nt_chancerain'     : '45',
                  'nt_chancesleet'    : '45',
                  'nt_chancesnow'     : '46',
                  'nt_chancetstorms'  : '47',
                  'clear skies'          : '31',
                  'nt_cloudy'         : '27',
                  'nt_flurries'       : '46',
                  'nt_fog'            : '20',
                  'freezingfog'            : '20',
                  'nt_hazy'           : '21',
                  'nt_mostlycloudy'   : '27',
                  'nt_mostlysunny'    : '33',
                  'partlycloudynight'   : '29',
                  'nt_partlysunny'    : '33',
                  'nt_sleet'          : '45',
                  'nt_rain'           : '45',
                  'showers-night	'           : '45',
                  'heavyrainswrsnight'           : '45',
                  'isorainswrsnight'           : '45',
                  'nt_snow'           : '46',
                  'isosnowswrsnight'           : '46',
                  'isosnowswrsday'           : '41',
                  'isosnowtswrsday'           : '41',
                  'isosnowtswrsnight'           : '46',
                  'nt_sunny'          : '31',
                  'nt_tstorms'        : '47',
                  'thunder-showers-night'        : '47',
                  'nt_unknown'        : 'na',
                  'nt_'               : 'na'}


def c_to_f(celsius: float) -> float:
    return round(celsius * 9 / 5 + 32)   


def get_temp_unit():
    """Returns 'F' or 'C' based on user's Kodi Regional setting."""
    return "C" if "C" in xbmc.getRegion("tempunit") else "F"

def format_temp(celsius):
    unit = get_temp_unit()
    if unit == "F":
        return f"{round(celsius * 9/5 + 32)}°F"
    return f"{round(celsius)}°C"   

def get_speed_unit():
    """Returns 'mph' or 'km/h'."""
    return "km/h" if "km" in xbmc.getRegion("speedunit") else "mph"

def format_speed(kmh):
    unit = get_speed_unit()
    if unit == "mph":
        return f"{round(kmh * 0.621371)} {unit}"
    return f"{round(kmh)} {unit}"   
