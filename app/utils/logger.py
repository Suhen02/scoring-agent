

import logging
import sys
from datetime import datetime


def setup_logger(name: str = "candidate_intelligence", level: int = logging.INFO) -> logging.Logger:
   
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)


    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        fh = logging.FileHandler(f"/tmp/genotek-ai-agent/output/pipeline_{timestamp}.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        logger.warning("Could not create log file, using console only")

    return logger


log = setup_logger()
