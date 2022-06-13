import logging
import threading

#for mumble
import pymumble_py3 as pymumble

#for vox
import pyaudio
from sys import byteorder
from array import array
from struct import pack
import time

class RemotePMR():
    """
    RemotePMR Class for connecting a PMR446 Handheld with a mumble server
    """

    SILENCE_THRESHOLD = 5000
    RECORD_AFTER_SILENCE_SECS = 5
    RATE = 44100
    MAXIMUMVOL = 32767
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16

    def __init__(self, options):
        logging.debug("Creating RemotePMR")
        self.mumble_setup(options)
        self.mumble_start(options)

        x = threading.Thread(target=self.pmr_working, args=(options,))
        x.start()
        x.join()

    def sound_received_handler(self, user, soundchunk):
        print('play sound received from mumble server upon its arrival')
        #stream.write(soundchunk.pcm)

    def mumble_setup(self, options):
        self.mumble = pymumble.Mumble(options.host, options.user, port=options.port, password=options.password,
                                      debug=False)
        self.mumble.callbacks.set_callback(pymumble.callbacks.PYMUMBLE_CLBK_SOUNDRECEIVED, self.sound_received_handler)
        self.mumble.set_receive_sound(1)  # Enable receiving sound from mumble server
        #self.mumble.set_codec_profile("audio")

    def mumble_start(self, options):
        self.mumble.start()  # start the mumble thread
        self.mumble.is_ready()  # wait for the connection

    def pmr_working(self, options):
        while 1:
            print ('vox wait')
            idle = self.pmr_vox_wait()
            print ('record')
            sample_width, data, wav_filename = self.pmr_record()
            data = pack('<' + ('h'*len(data)), *data)
            print ('send')
            self.mumble.sound_output.add_sound(data)
            #wf = wave.open(wav_filename, 'wb')
            #wf.setnchannels(1)
            #wf.setsampwidth(sample_width)
            #wf.setframerate(RATE)
            #wf.writeframes(data)
            #wf.close()
            #print()
            #recinfo = 'Recording finished. Saved to: %s' % (wav_filename)
            #print(recinfo)
        return True

    def mumble_send(self):
        return True

    def pmr_vox_wait(self):
        # Wait until vox is recognized
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=1, rate=self.RATE,
            input=True, output=True,
            frames_per_buffer=self.CHUNK_SIZE)

        record_started_stamp = 0
        wav_filename = ''
        record_started = False

        while 1:
            # little endian, signed short
            snd_data = array('h', stream.read(self.CHUNK_SIZE))
            if byteorder == 'big':
                snd_data.byteswap()

            voice = self.pmr_vox_detected(snd_data)
            #show_status(snd_data, record_started, record_started_stamp, wav_filename)
            print ('vox wait')
            del snd_data

            if voice:
                break
            
        stream.stop_stream()
        stream.close()
        p.terminate()
        return True

    def pmr_vox_detected(self, snd_data):
        "Returns 'True' if sound peaked above the 'silent' threshold"
        return max(snd_data) > self.SILENCE_THRESHOLD

    def pmr_record(self):
        """
        Record audio when activity is detected 

        Normalizes the audio, trims silence from the 
        start and end, and pads with 0.5 seconds of 
        blank sound to make sure VLC et al can play 
        it without getting chopped off.
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=1, rate=self.RATE,
            input=True, output=True,
            frames_per_buffer=self.CHUNK_SIZE)

        num_silent = 0
        record_started_stamp = 0
        last_voice_stamp = 0
        wav_filename = ''
        record_started = False

        r = array('h')

        while 1:
            # little endian, signed short
            snd_data = array('h', stream.read(self.CHUNK_SIZE))
            if byteorder == 'big':
                snd_data.byteswap()
            r.extend(snd_data)

            voice = self.pmr_vox_detected(snd_data)

            if voice and record_started:
                last_voice_stamp = time.time()
            elif voice and not record_started:
                record_started = True
                record_started_stamp = last_voice_stamp = time.time()
            
            if record_started and time.time() > (last_voice_stamp + self.RECORD_AFTER_SILENCE_SECS):
                break

        sample_width = p.get_sample_size(self.FORMAT)
        stream.stop_stream()
        stream.close()
        p.terminate()

        #r = normalize(r)
        #r = trim(r)
        #r = add_silence(r, 0.5)
        return sample_width, r, wav_filename