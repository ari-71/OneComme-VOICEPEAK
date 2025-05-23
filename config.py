# .env ファイルをロードして環境変数へ反映
from dotenv import load_dotenv
from setuptools._distutils.util import strtobool

load_dotenv(override = True)

# 環境変数を参照
import os
VOICE_NARRATOR = 'Japanese Female 1' if os.getenv('VOICE_NARRATOR') == None else os.getenv('VOICE_NARRATOR')
# mac 
# VOICE_VOLUME = '0.15' if os.getenv('VOICE_VOLUME') == None else os.getenv('VOICE_VOLUME')
VOICE_VOLUME = '50' if os.getenv('VOICE_VOLUME') == None else os.getenv('VOICE_VOLUME')

EMOTION_HAPPY = '0' if os.getenv('EMOTION_HAPPY') == None else os.getenv('EMOTION_HAPPY')
EMOTION_SAD = '0' if os.getenv('EMOTION_SAD') == None else os.getenv('EMOTION_SAD')
EMOTION_FUN = '0' if os.getenv('EMOTION_FUN') == None else os.getenv('EMOTION_FUN')
EMOTION_ANGRY = '0' if os.getenv('EMOTION_ANGRY') == None else os.getenv('EMOTION_ANGRY')
EMOTION_BOSOBOSO = '0' if os.getenv('EMOTION_BOSOBOSO') == None else os.getenv('EMOTION_BOSOBOSO')
EMOTION_DOYARU = '0' if os.getenv('EMOTION_DOYARU') == None else os.getenv('EMOTION_DOYARU')
EMOTION_HONWAKA = '0' if os.getenv('EMOTION_HONWAKA') == None else os.getenv('EMOTION_HONWAKA')
EMOTION_TEARY = '0' if os.getenv('EMOTION_TEARY') == None else os.getenv('EMOTION_TEARY')
EMOTION_OCHOUSHIMONO = '0' if os.getenv('EMOTION_OCHOUSHIMONO') == None else os.getenv('EMOTION_OCHOUSHIMONO')
EMOTION_COMMENT = True if os.getenv('EMOTION_COMMENT') == None else os.getenv('EMOTION_COMMENT')
SEX_COMMENT = True if os.getenv('SEX_COMMENT') == None else os.getenv('SEX_COMMENT')

MAX_NUM_CHARACTERS = 136 if os.getenv('MAX_NUM_CHARACTERS') == None else int(os.getenv('MAX_NUM_CHARACTERS'))
DEBUG_FLAG = False if os.getenv('DEBUG_FLAG') == None else bool(strtobool(os.getenv('DEBUG_FLAG')))
EXCEPTION_OUTPUT_VOICE_FILEPATH = os.getenv('EXCEPTION_OUTPUT_VOICE_FILEPATH')
MAX_RETRY = 3 if os.getenv('MAX_RETRY') == None else int(os.getenv('MAX_RETRY'))
VOICEPEAK_APP_FILEPATH = 'C:\\Program Files\\VOICEPEAK\\voicepeak.exe' if os.getenv('VOICEPEAK_APP_FILEPATH') == None else os.getenv('VOICEPEAK_APP_FILEPATH')
PLAYER_FILEPATH = '%USERPROFILE%\\AppData\\Local\\Microsoft\\WinGet\\Links\\ffplay.exe' if os.getenv('PLAYER_FILEPATH') == None else os.getenv('PLAYER_FILEPATH')
OUTPUT_VOICE_DIRPATH = '%TEMP%' if os.getenv('OUTPUT_VOICE_DIRPATH') == None else os.getenv('OUTPUT_VOICE_DIRPATH')
# mac 
# VOICEPEAK_APP_FILEPATH = '/Applications/voicepeak.app/Contents/MacOS/voicepeak' if os.getenv('VOICEPEAK_APP_FILEPATH') == None else os.getenv('VOICEPEAK_APP_FILEPATH')
# PLAYER_FILEPATH = '/usr/bin/afplay' if os.getenv('PLAYER_FILEPATH') == None else os.getenv('PLAYER_FILEPATH')
# OUTPUT_VOICE_DIRPATH = '/tmp' if os.getenv('OUTPUT_VOICE_DIRPATH') == None else os.getenv('OUTPUT_VOICE_DIRPATH')
