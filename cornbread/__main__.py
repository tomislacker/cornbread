"""
cornbread - Daemon to track your window focus

Usage:
    cornbread daemon [options]
    cornbread process [options]

Options:
    -l, --log-level=L   Logging module level [default: debug]
"""
import logging


log = logging.getLogger("cornbread")


if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__)

    logging.basicConfig(**{
        "level": getattr(logging, args['--log-level'].upper()),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    })

    import json
    log.debug(":\n" + json.dumps(args, indent=4, sort_keys=True))

    raise NotImplementedError
