import logging

# for mumble
import pymumble_py3 as pymumble

# for vox
import pyaudio
from sys import byteorder
from array import array
import time
from threading import Thread, Lock

# time
from datetime import datetime, timedelta
import asyncio

class RemotePMR():
    """
    RemotePMR Class for connecting a PMR446 Handheld with a mumble server
    """

    SILENCE_THRESHOLD = 5000
    RECORD_AFTER_SILENCE_SECS = 3
    RATE = 44100
    MAXIMUMVOL = 32767
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16

    def __init__(self, options):
        logging.debug("Creating RemotePMR")
        self.mumble_setup(options)

        self.mutex = Lock()
        self.time = 0
        self.task = None

        p = pyaudio.PyAudio()
        self.stream = p.open(format=self.FORMAT, channels=1, rate=self.RATE,
            input=True, output=True,
            frames_per_buffer=self.CHUNK_SIZE)

        self.mumble_start(options)

        self.x = Thread(target=self.pmr_working, args=(options,))
        self.x.daemon = True
        self.x.start()
        self.x.join()
    
    def func(self, num):
        while 1:
            if time.time() > self.time:
                print("Port Low")
                self.task = None
                break
            else:
                time.sleep(self.time - time.time())

    def sound_received_handler(self, user, soundchunk):
        self.mutex.acquire()
        self.time = time.time() + 2 #sec
        if self.task == None:
            self.task = Thread(target=self.func, args=(42,))
            self.task.daemon = True
            self.task.start()
            print("Port High")
            time.sleep(0.5)
        self.stream.write(soundchunk.pcm)
        self.mutex.release()

    def mumble_setup(self, options):
        self.mumble = pymumble.Mumble(options.host, options.user, port=options.port, password=options.password,
                                      debug=False)
        self.mumble.callbacks.set_callback(pymumble.callbacks.PYMUMBLE_CLBK_SOUNDRECEIVED, self.sound_received_handler)
        self.mumble.set_receive_sound(1)  # Enable receiving sound from mumble server

    def mumble_start(self, options):
        self.mumble.start()  # start the mumble thread
        self.mumble.is_ready()  # wait for the connection

    def pmr_working(self, options):
        while 1:
            self.pmr_vox_wait()
            self.pmr_send()

    def pmr_vox_wait(self):
        # Wait until vox is recognized
        while 1:
            self.mutex.acquire()
            snd_data = array('h', self.stream.read(self.CHUNK_SIZE))
            self.mutex.release()
            voice = self.pmr_vox_detected(snd_data)
            del snd_data

            if voice:
                break

    def pmr_vox_detected(self, snd_data):
        # Returns 'True' if sound peaked above the 'silent' threshold
        return max(snd_data) > self.SILENCE_THRESHOLD

    def pmr_send(self):
        #Send audio when activity is detected 
        last_voice_stamp = 0
        record_started = False

        while 1:
            # little endian, signed short
            self.mutex.acquire()
            snd_data = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
            self.mutex.release()
            wf_data = array('h', snd_data)

            voice = self.pmr_vox_detected(wf_data)
            del wf_data

            self.mumble.sound_output.add_sound(snd_data)
            del snd_data

            if voice and record_started:
                last_voice_stamp = time.time()
            elif voice and not record_started:
                record_started = True
                last_voice_stamp = time.time()

            if record_started and time.time() > (last_voice_stamp + self.RECORD_AFTER_SILENCE_SECS):
                break