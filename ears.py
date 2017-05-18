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

'''


import speech_recognition as sr
from utils import noalsaerr
import constants


class Ear():

    def __init__(self, responder=None, lquit=''):
        self._recog = sr.Recognizer()
        self._audio = None
        self._text = ''
        self._last_text = ''
        self._lual_quit = lquit if lquit else constants.LUAL_QUIT
        self._responder = responder  # function to use for answer

    def lual(self, accepted=constants.ACCEPTED, out=True):

        while True:
            self.listen(False)
            self.understand()
            if self._text == self._lual_quit: break
            self._post_process_text(accepted)
            self.answer(self._text)
            if out: print(self._text)

    def listen(self, result=True, adjust=True, report=True):

        with noalsaerr() as n, sr.Microphone() as source:
            if adjust: self._recog.adjust_for_ambient_noise(source)
            if report: print(constants.EARS_LISTENING)
            self._audio = self._recog.listen(source)
        if result: return understand()  # for listen-specific call

    def understand(self, audio=None, report=True):
        if report: print(constants.EARS_UNDERSTANDING)
        if audio: self._audio = audio
        self._last_text = self._text

        try:
            self._text = self._recog.recognize_sphinx(self._audio).lower()

        except sr.UnknownValueError:
            print("Sphinx didn't understand anything you said...")
            return None

        except sr.RequestError as e:
            print("Sphinx error: {0}".format(e))
            return None
        return self._text

    def answer(self, *args, report=True):
        result = None

        try:
            if self._responder: result = self._responder(*args)

        except Exception as e:
            print('Error: unable to answer; %s' % str(e))
            return None
        return result

    def _post_process_text(self, accepted=constants.ACCEPTED):
        text = self._text

        for char in text:

            if not char in accepted:
                text.replace(char, '')
        self._text = text
