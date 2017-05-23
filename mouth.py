# This file is part of ClIDE
# ClIDE - A live-modifiable command-line IDE that can accept commands as pseudocode  

# @author Andrew Phillips  
# @copyright 2017 Andrew Phillips <skeledrew@gmail.com>

# ClIDE is free software; you can redistribute it and/or
# modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
# License as published by the Free Software Foundation; either
# version 3 of the License, or any later version.

# ClIDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU AFFERO GENERAL PUBLIC LICENSE for more details.

# You should have received a copy of the GNU Affero General Public
# License along with ClIDE.  If not, see <http://www.gnu.org/licenses/>.

'''
17-05-23
  - MaryTTS code template from https://github.com/marytts/marytts-txt2wav/blob/python/txt2wav.py
  - PyAudio code template from http://people.csail.mit.edu/hubert/pyaudio/docs/
'''

from utils import pesh, hash_sum
import httplib2
from urllib.parse import urlencode, quote
import constants
import os
import pyaudio, wave, time
from io import BytesIO


class Voice():

    def __init__(self, path=''):
        self._path = path if path else constants.MARY_TTS_PATH
        self._mary_host = 'localhost'
        self._mary_port = '59125'
        self._cache = {}
        if not os.path.exists(constants.SPOKEN_WORDS_PATH): os.makedirs(constants.SPOKEN_WORDS_PATH)

    def mary_alive(self):
        # TODO: check if the service is running
        return True

    def speak(self, text):
        self._text = text

        if self._search_cache(text):
            self.playback(self._cache[text])
            return
        if not self.mary_alive(): return
        self.mary_tts(text)
        self.playback()
        return

    def mary_tts(self, text):
        query_hash = {"INPUT_TEXT": text,
                      "INPUT_TYPE": "TEXT",
                      "LOCALE": "en_US",
                      "VOICE": "cmu-slt-hsmm", # Voice informations  (need to be compatible)
                      "OUTPUT_TYPE": "AUDIO",
                      "AUDIO": "WAVE", # Audio informations (need both)
                      }
        query = urlencode(query_hash)
        #print("query = \"http://%s:%s/process?%s\"" % (self._mary_host, self._mary_port, query))

        # Run the query to mary http server
        h_mary = httplib2.Http()
        resp, content = h_mary.request("http://%s:%s/process?" % (self._mary_host, self._mary_port), "POST", query)

        #  Decode the wav file or raise an exception if no wav files
        if (resp["content-type"] == "audio/x-wav"):
            #self._c_bytes = BytesIO(content)
            self._cache[text] = content #self._c_bytes
            h_text = hash_sum(text)
            spch_file = '%sspch-%s.wav' % (constants.SPOKEN_WORDS_PATH, h_text)

            with open(spch_file, 'wb') as so:
                so.write(content)

        else:
            raise Exception(content)
        return content

    def playback(self, f_name=''):
        if not f_name: f_name = self._cache[self._text]
        if isinstance(f_name, bytes): f_name = BytesIO(f_name)
        wf = wave.open(f_name, 'rb')
        self._wf = wf
        p = pyaudio.PyAudio()
        self._pa = p
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=self._callback)
        self._stream = stream
        stream.start_stream()
        return

    def _callback(self, in_data, frame_count, time_info, status):
        # allows for async playback
        data = self._wf.readframes(frame_count)

        if not len(data) > 0:
            # clean up when playing is complete
            self._stream.stop_stream()
            self._stream.close()
            self._pa.terminate()
            return
        return (data, pyaudio.paContinue)

    def _search_cache(self, text):
        # searches the memory and stored cache
        if text in self._cache: return True
        h_text = hash_sum(text)
        spch_file = '%sspch-%s.wav' % (constants.SPOKEN_WORDS_PATH, h_text)

        if os.path.exists(spch_file):

            with open(spch_file, 'rb') as so:
                # place into cache
                self._cache[text] = so.read()
                return True
        return False
