import logging
import pymumble_py3 as pymumble

class RemotePMR():
    """
    RemotePMR Class for connecting a PMR446 Handheld with a mumble server
    """

    def __init__(self, options):
        logging.debug("Creating RemotePMR")
        self.mumble_setup(options)
        self.mumble_start(options)

    def message_received(self, text):
        logging.error("Incoming Message - NOT IMPLEMENTED YET")

    def mumble_setup(self, options):
        self.mumble = pymumble.Mumble(options.host, options.user, port=options.port, password=options.password,
                                      debug=False)
        self.mumble.callbacks.set_callback("text_received", self.message_received)

        self.mumble.set_codec_profile("audio")

    def mumble_start(self, options):
        self.mumble.start()  # start the mumble thread
        self.mumble.is_ready()  # wait for the connection

    def mumble_working(self, options):
        return True

    def mumble_send(self):
        return True