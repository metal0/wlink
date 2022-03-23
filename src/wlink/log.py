import logging
from loguru import logger

logging.basicConfig(level='INFO')

def configure_log(logger=logger, packets_level=5, events_level=15, messages_level=20):
	logger.configure()
	logger.level('PACKETS', no=packets_level, color='<blue>', icon='PACKETS')
	logger.level('EVENTS', no=events_level, color='<cyan>', icon='EVENTS')
	logger.level('MESSAGES', no=messages_level, color='<green>', icon='MESSAGES')

configure_log(packets_level=5)
