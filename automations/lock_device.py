import ctypes

from pyttsx3 import speak

keywords = ["lock", "lock computer", " lock device"]

speak("locking the device")
ctypes.windll.user32.LockWorkStation()
