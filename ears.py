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


class Ear():

    def __init__(self):
        pass

    def lual(self):
        pass

    def listen(self):
        self._recog = sr.Recognizer()
        self._audio = None
        self._text = None

        with sr.Microphone() as source:
            self._recog.adjust_for_ambient_noise(source)
            print('I\'m listening...')
            self._audio = self._recog.listen(source)
            print('Sending audio for processing!')

        try:
            self._text = self._recog.recognize_sphinx(self._audio)

        except sr.UnknownValueError:
            print("Sphinx didn't understand anything you said...")

        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
        return self._text
