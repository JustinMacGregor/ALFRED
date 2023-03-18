import json
import os
import queue
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

import pyttsx3
import sounddevice as sd
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
    with open("automations.json") as f:
        automations = json.load(f)
        for automation in automations["automations"]:
            automation_list.insert(tk.END, automation["title"])


# call the function to populate the list box initially
populate_automation_list()


# function to delete an automation from the list box and the file system
def delete_automation():
    selection = automation_list.curselection()
    if selection:
        automation_index = selection[0]
        with open("automations.json") as f:
            automations = json.load(f)
            automation = automations["automations"][automation_index]
            if messagebox.askyesno("Delete Automation", f"Are you sure you want to delete {automation['title']}?"):
                os.remove(automation["py_file_path"])
                automations["automations"].pop(automation_index)
                with open("automations.json", "w") as f:
                    json.dump(automations, f, indent=4)
                populate_automation_list()


# create a button to delete selected automation
delete_button = tk.Button(window, text="Delete Automation", command=delete_automation)
delete_button.pack(pady=10)


def add_automation():
    # open a file dialog to select the automation file
    file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if file_path:
        # ask for the automation metadata
        title = simpledialog.askstring("Add Automation", "Enter the title of the automation:")
        description = simpledialog.askstring("Add Automation", "Enter a description of the automation:")
        trigger_words = simpledialog.askstring("Add Automation",
                                               "Enter the trigger words for the automation (comma-separated):")
        trigger_words = [word.strip() for word in trigger_words.split(",")]
        # add the new automation to the JSON file
        with open("automations.json") as f:
            automations = json.load(f)
        new_automation = {"title": title, "description": description, "trigger_words": trigger_words,
                          "py_file_path": file_path}
        automations["automations"].append(new_automation)
        with open("automations.json", "w") as f:
            json.dump(automations, f, indent=4)
        populate_automation_list()


# create a button to add a new automation
add_button = tk.Button(window, text="Add Automation", command=add_automation)
add_button.pack(pady=10)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def UseMicrophone():
    r = sr.Recognizer()

    def recognize(q, trigger_words, automations):
        with sr.Microphone(device_index=device_combobox.current()) as source:
            r.adjust_for_ambient_noise(source)
            print("Listening...")
            timeout_duration = 5  # wait for a maximum of 5 seconds for the next command
            last_command_time = 0  # keep track of the time of the last command
            while True:
                # listen for the duration of the timeout
                audio = r.listen(source, timeout=timeout_duration)
                try:
                    result = r.recognize_google(audio)
                    print("Recognizing...")
                    print("result2:")
                    print(result)
                    if any(word in result.lower() for word in trigger_words):
                        # only execute the automation if there has been sufficient time since the last command
                        current_time = time.time()
                        if current_time - last_command_time >= timeout_duration:
                            # Find the automation that matches the trigger word(s)
                            for automation in automations["automations"]:
                                if all(word in result.lower() for word in automation["trigger_words"]):
                                    # Execute the automation's Python file
                                    os.system(f'python {automation["py_file_path"]}')
                                    speak("Task completed!")
                                    last_command_time = current_time
                                    break
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    speak("Sorry, I could not process your request at the moment. Please try again later.")

                # exit the loop after 5 seconds
                if not q.empty():
                    break

    def start_recognizer():
        with open("automations.json") as f:
            automations = json.load(f)
        trigger_words = []
        for automation in automations["automations"]:
            trigger_words.extend(automation["trigger_words"])

        qu = queue.Queue()
        t = threading.Thread(target=recognize, args=(qu, trigger_words, automations))
        t.start()

    window.after(100, start_recognizer)


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
            query = UseMicrophone().lower()
            if query:
                with open("automations.json") as f:
                    automations = json.load(f)
                    for automation in automations["automations"]:
                        if any(word in query for word in automation["trigger_words"]):
                            speak(f"Running {automation['title']}")
                            os.system(f"python {automation['py_file_path']}")
                            break


    def main_loop():
        window.update()
        window.after(100, main_loop)


    # Start the threads
    threading.Thread(target=take_command).start()
    window.after(100, main_loop)
    window.mainloop()
