import xbmc

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
                  'clear'             : '31',
                  'cloudy'            : '26',
                  'overcast'            : '26',
                  'cloudy skies'            : '26',
                  'flurries'          : '13',
                  'fog'               : '20',
                  'hazy'              : '21',
                  'mostlycloudy'      : '28',
                  'mostlysunny'       : '34',
                  'partlycloudy'      : '30',
                  'partcloudrainthunder'      : '30',
                  'partcloudrainthunderday'      : '30',
                  'partcloudrainthundernight'      : '47',
                  'partlycloudyday'      : '30',
                  'partlycloudynight'      : '33',
                  'partlysunny'       : '34',
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
                  'snow'              : '42',
                  'modsnow'              : '42',
                  'modsnowswrsday'              : '42',
                  'modsnowswrsnight'              : '46',
                  'cloudsleetsnowthunder'              : '6',
                  'heavysnow'              : '42',
                  'modsnow'              : '42',
                  'occlightsnow'              : '14',
                  'blizzard'              : '15',
                  'sunny'             : '32',
                  'sunny skies'             : '32',
                  'cloudrainthunder'           : '38',
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
                  'heavyrainswrsnight'           : '45',
                  'isorainswrsnight'           : '45',
                  'nt_snow'           : '46',
                  'isosnowswrsnight'           : '46',
                  'isosnowswrsday'           : '41',
                  'isosnowtswrsday'           : '41',
                  'isosnowtswrsnight'           : '46',
                  'nt_sunny'          : '31',
                  'nt_tstorms'        : '47',
                  'nt_unknown'        : 'na',
                  'nt_'               : 'na'}

