import logging
import argparse

class RemotePMR():
    """
    MQTTClient implementation using asyncio-mqtt client.
    """

    def __init__(self, options):
        return


# main entry point
if __name__ == "__main__":
    #default logger
    FORMAT = '%(asctime)s %(levelname)s:%(message)s'
    logging.basicConfig(format=FORMAT)
    _LOG = logging.getLogger(__name__)

    #default parser
    parser = argparse.ArgumentParser(description='Connect to mumble server and controll remote pmr446 handheld')
    parser.add_argument('-i', '--input', help='input audio device', default="hw:0,0")
    parser.add_argument('-o', '--output', help='output audio device', default="hw:0,0")
    parser.add_argument('-a', '--address', help='host address of mumble server', default="localhost")
    parser.add_argument('-p', '--port', help='host port of mumble server', default="47854")
    parser.add_argument('-v', '--verbose', action='store_true', help='more output')
    args = parser.parse_args()

    if args.verbose:
        _LOG.setLevel(logging.DEBUG) 

    _LOG.debug("Args: "+str(args))

    #