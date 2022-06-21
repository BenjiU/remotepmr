import logging
import argparse
from remotepmr import RemotePMR

# main entry point
if __name__ == "__main__":
    #default parser
    parser = argparse.ArgumentParser(description='Connect to mumble server and controll remote pmr446 handheld')
    parser.add_argument('-i', '--input', help='input audio device', default="hw:0,0")
    parser.add_argument('-o', '--output', help='output audio device', default="hw:0,0")
    parser.add_argument('-H', '--host', help='host address of mumble server', default="127.0.0.1")
    parser.add_argument('-P', '--port', help='host port of mumble server', type=int, default="64738")
    parser.add_argument('-u', '--user', help='username for mumble server', default="remotepmr")
    parser.add_argument('-p', '--password', help='credential for mumble server', default="")
    parser.add_argument('-g', '--gpio_tx', help='gpio used to activate tx on pmr', default="19")
    parser.add_argument('-v', '--verbosity', help='less or more output', default="INFO", metavar="LEVEL", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    args = parser.parse_args()

    #default logger
    FORMAT = '%(asctime)s [%(filename)15s:%(lineno)4s - %(funcName)15s()] %(levelname)s: %(message)s'
    logging.basicConfig(format=FORMAT, level=args.verbosity)
    logging.debug("parsed args: "+str(args))

    #create the RemotePMR object with the attributes
    logging.info("Starting RemotePMR:")
    RemotePMR(args)