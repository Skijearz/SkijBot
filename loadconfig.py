import os

configFile = os.path.join('.','config','config.py')

if os.path.isfile(configFile):
    try:
        from config.config import __token__
    except ImportError:
        raise Exception('__token__ variable MUST be set')
    try:
        from config.config import __prefix__
    except ImportError:
        raise Exception('__prefix__ variable MUST be set')
        