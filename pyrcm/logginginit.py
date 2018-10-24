import logging
import sys

class BasicLoggingInitializer(object):

    FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LVL = logging.INFO
    QUIET = ['engineio']

    @classmethod
    def shush(cls, loggingid, lvl=logging.WARN):
        logging.getLogger(loggingid).setLevel(lvl)

    @classmethod
    def init(cls):
        logger = logging.getLogger()
        logger.level = cls.LVL
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(cls.FMT)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        for loggingid in cls.QUIET:
            cls.shush(loggingid)
BasicLoggingInitializer.init()
