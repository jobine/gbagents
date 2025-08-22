import sys
from loguru import logger

log_format = '<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'

logger.remove()

logger.add(sys.stderr, level='DEBUG', format=log_format, colorize=True)
logger.add(sys.stderr, level='ERROR', format=log_format, colorize=True)

logger.add('logs/app.log', rotation='1 MB', level='DEBUG', format=log_format, colorize=False)

LOG = logger

__all__ = ['LOG']
