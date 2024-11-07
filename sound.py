from kivy.core.audio import SoundLoader

class Play:
    def beep(self, *args):
        sound = SoundLoader.load('alert_sound.mp3')
        if sound:
            sound.play()
        print("Beep sound played")    