keywords = ["lock computer", " lock device"]

speak("locking the device")
ctypes.windll.user32.LockWorkStation()
