import ctypes
import os
import sounddevice as sd
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import pyttsx3
import speech_recognition as sr

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# create GUI window
window = tk.Tk()
window.title("Python Automations")
window.geometry("500x500")

# create a list box to show existing automations
automation_list = tk.Listbox(window, width=50)
automation_list.pack(pady=20)

# create a label for the dropdown menu
device_label = tk.Label(window, text="Select Input Device:")
device_label.pack(pady=10)

# create a dropdown menu for selecting the input audio device
device_var = tk.StringVar()
devices = sd.query_devices()
device_names = [device["name"] for device in devices]
device_combobox = ttk.Combobox(window, textvariable=device_var, values=device_names)
device_combobox.current(0)  # set the default value to the first device in the list
device_combobox.pack()


# function to populate the list box with existing automations
def populate_automation_list():
    automation_list.delete(0, tk.END)  # clear the list box
    automation_folder = os.path.join(os.getcwd(), "automations")
    automations = os.listdir(automation_folder)
    for automation in automations:
        if automation.endswith(".py"):
            automation_list.insert(tk.END, automation)


# call the function to populate the list box initially
populate_automation_list()


# function to delete an automation from the list box and the file system
def delete_automation():
    selection = automation_list.curselection()
    if selection:
        automation = automation_list.get(selection[0])
        if messagebox.askyesno("Delete Automation", f"Are you sure you want to delete {automation}?"):
            automation_path = os.path.join(os.getcwd(), "automations", automation)
            os.remove(automation_path)
            populate_automation_list()


# create a button to delete selected automation
delete_button = tk.Button(window, text="Delete Automation", command=delete_automation)
delete_button.pack(pady=10)


def add_automation():
    # open a file dialog to select the automation file
    file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if file_path:
        # ask for the trigger phrase
        phrase = simpledialog.askstring("Add Automation", "Enter the phrase to trigger this automation:")
        if phrase:
            # create the automation file in the automations folder
            automation_folder = os.path.join(os.getcwd(), "automations")
            automation_name = os.path.basename(file_path)
            new_automation_path = os.path.join(automation_folder, automation_name)
            with open(file_path, "r") as f:
                content = f.read()
                print(content)
            with open(new_automation_path, "w") as f:
                words = phrase.lower().split(",")
                words_str = ', '.join(f'"{word}"' for word in words)
                f.write(f'keywords = [{words_str}]\n\n')
                f.write(f'{content}\n')

            populate_automation_list()


# create a button to add a new automation
add_button = tk.Button(window, text="Add Automation", command=add_automation)
add_button.pack(pady=10)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def takeCommand():
    r = sr.Recognizer()

    with sr.Microphone(device_index=device_combobox.current()) as source:

        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        print(e)
        print("Unable to Recognize your voice.")
        return "None"

    return query


if __name__ == '__main__':
    clear = lambda: os.system('cls')

    # This Function will clean any
    # command before execution of this python file
    clear()

    automation_folder = os.path.join(os.getcwd(), "automations")

    # Check if the "automations" folder exists, create it if it doesn't
    if not os.path.exists(automation_folder):
        os.mkdir(automation_folder)


    def take_command():
        while True:
            query = takeCommand().lower()

            # check if query matches any trigger phrase for an automation
            automation_folder = os.path.join(os.getcwd(), "automations")
            automations = os.listdir(automation_folder)
            for automation in automations:
                if automation.endswith(".py"):
                    automation_path = os.path.join(automation_folder, automation)
                    with open(automation_path, "r") as f:
                        content = f.read()
                    if f'"{query.lower()}"' in content:
                        speak(f"Running {automation}")
                        os.system(f"python {automation_path}")
                        break

            # example2
            if 'lock' in query:
                speak("locking the device")
                ctypes.windll.user32.LockWorkStation()

    def main_loop():
        window.update()
        window.after(100, main_loop)

    # Start the threads
    threading.Thread(target=take_command).start()
    window.after(100, main_loop)
    window.mainloop()