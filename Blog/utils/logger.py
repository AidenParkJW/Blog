import logging
logger = logging.getLogger("django")

class Logger():
    
    def __init__(self, params):
        pass
    
    @staticmethod
    def info(*args):
        
        logger.info("\n")
        logger.info("--" * 50)
        
        for str in args:
            logger.info(str)
            
        logger.info("--" * 50)
        logger.info("\n")