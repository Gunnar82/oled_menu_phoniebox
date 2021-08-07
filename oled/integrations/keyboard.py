import keyboard

class KeyboardCtrl():

    def __init__(self, loop, turn_callback, push_callback):
        self.loop = loop
        self.turn_callback = turn_callback
        self.push_callback = push_callback


        keyboard.add_hotkey('Esc', lambda: self.push_callback())

        keyboard.add_hotkey('Right', lambda: self.turn_right())
        keyboard.add_hotkey('Left', lambda: self.turn_left())
        keyboard.add_hotkey('Up', lambda: self.turn_up())
        keyboard.add_hotkey('Down', lambda: self.turn_down())



    def turn_left(self):
        self.turn_callback(-1, _key='left')


    def turn_right(self):
        self.turn_callback(1, _key='right')

    def turn_up(self):
        self.turn_callback(-1, _key='up')


    def turn_down(self):
        self.turn_callback(1, _key='down')

    def pushlong_callback(self):
        print ("long2")

        self.push_callback(_lp=True)
