from bossanova808 import exception_logger
from resources.lib import jellyfin_fixer

if __name__ == "__main__":
    with exception_logger.log_exception():
        jellyfin_fixer.run()
