import logging
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    # '%(log_color)s%(levelname)s:%(name)s:%(message)s')
    '%(relativeCreated)09.0f [%(log_color)s%(levelname)-7s] %(filename)s:%(lineno)s: %(message)s')
)

# logging.basicConfig(level='DEBUG')  # , format='\033[95m%(relativeCreated)-13s [%(levelname)-7s]\033[0m \033[92m%(filename)s:%(lineno)s:\033[0m %(message)s')

logger = logging.getLogger('pwm')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

debug = logger.debug
info = logger.info
warn = logger.warn
error = logger.error
exception = logger.exception
