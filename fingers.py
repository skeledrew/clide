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


from pynput.mouse import Button, Controller as MouseControl
from pynput.keyboard import Key, Controller as KbdControl


class Finger():

    def __init__(self, speed=10):
        self._mse = MouseControl()
        self._kbd = KbdControl()
        self._speed = speed

    def type(self, keys):
        self._kbd.type(keys)

    def move(self, dx, dy, type_='abs'):

        if type_ == 'abs':
            self._mse.position = (dx, dy)

        else:
            self._mse.move(dx, dy)

    def click(self, button='left', count=1):
        button = getattr(Button, button, 'left')
        self._mse.click(button, count)

    def scroll(self, vscr=2, hscr=0):
        self._mse.scroll(hscr, vscr)

    def drag(self, to=(), frm=(), button='left'):
        # simulate a drag. TODO: make in increments instead of instant
        if not frm: frm = self._mse.position
        if not to: to = self._mse.position
        button = getattr(Button, button, 'left')
        self._mse.press(button)
        self._mse.position = to
        self._mse.release(button)

        #while not self._mse.position == to:
            # simulate movement one step at a time
            #x_pos = self._mse.position[0]
            #y_pos = self._mse.position[1]
            #if not x_pos == to[0]: x_pos

    def press(self, device='mouse', button='left'):

        if device == 'mouse':
            self._mse.press(getattr(Button, button, 'left'))

        else:
            key = button if len(button) == 1 else getattr(Key, button, 'space')
            self._kbd.press(key)

    def release(self, device='mouse', button='left'):
        # specify mouse or keyboard

        if device == 'mouse':
            self._mse.release(getattr(Button, button, 'left'))

        else:
            key = button if len(button) == 1 else getattr(Key, button, 'space')
            self._kbd.release(key)
