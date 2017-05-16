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
