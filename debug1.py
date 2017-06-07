import logging
import threading
from cornbread.xorg import *

if __name__ == '__main__':
    logging.warning('Creating FW')
    w = FocusedWindow()

    logging.warning('Creating FW thread')
    t = threading.Thread(target=FocusedWindowWatcher, args=(w,))

    logging.warning('Starting thread')
    t.start()

    try:
        logging.warning('Joining FW thread')
        t.join()

    except KeyboardInterrupt as e:
        logging.warning('Keyboard interrupt')
        w._exit_watch = True
        t.join(4)
