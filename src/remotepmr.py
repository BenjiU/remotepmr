import logging
import pymumble.pymumble_py3 as pymumble

class RemotePMR():
    """
    RemotePMR Class for connecting a PMR446 Handheld with a mumble server
    """

    def __init__(self, options):
        logging.debug("Creating RemotePMR")

        self.mumble = pymumble.Mumble(options.host, user=options.user, port=options.port, password=options.password,
                                      debug=options.verbosity)
        self.mumble.callbacks.set_callback("text_received", self.message_received)

        self.mumble.set_codec_profile("audio")
        self.mumble.start()  # start the mumble thread
        self.mumble.is_ready()  # wait for the connection

    def message_received(self, text):
        logging.error("Incoming Message - NOT IMPLEMENTED YET")
