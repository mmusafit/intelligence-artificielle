#importation de module 
import pyautogui
import speech_recognition as sr
import pyttsx3 as ttx
import time


# Initialiser le moteur de synthèse vocale
engine = ttx.init()

# Configurer la voix en français
engine.setProperty('voice', "french")
engine.setProperty('rate', 150)  # Ajuster la vitesse de la parole (peut être modifié)
engine.setProperty('volume', 1.0)  # Ajuster le volume (peut être modifié)


#function pour la reconnaissance vocale 
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        engine.say("Buongiorno, come posso aiutarvi?")
        engine.runAndWait()
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="it-IT")
        print(f"Commando vocale riconosciuto : {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("Non ho capito niente.")
        return None
    except sr.RequestError as e:
        print(f"Errore riconoscimento vocale  : {e}")
# Fonction pour le déplacement et le clic de la souris
def deplacer_souris(direction, action):
    x, y = pyautogui.position()
    if 'alto' in direction:
        pyautogui.moveTo(x, y - 50, duration=3)
    elif 'basso' in direction:
        pyautogui.moveTo(x, y + 50, duration=3)
    elif 'sinistra' in direction:
        pyautogui.moveTo(x - 50, y, duration=3)
    elif 'destra' in direction:
        pyautogui.moveTo(x + 50, y, duration=3)
    else:
        print("Direzione invalida")

    # Effectuer le clic
    if 'clicca' in action:
        if 'sinistra' in direction:
            pyautogui.click(button='left')
        elif 'destra' in direction:
            pyautogui.click(button='right')
        elif 'alto' in direction or 'basso' in direction:
            pyautogui.click()
        else:
            print("Azione di clic invalida")

# Fonction principale
def main():
    while True:
        command = recognize_speech()
        if command:
            parts = command.split()
            direction = [word for word in parts if word in ['alto', 'basso', 'sinistra', 'destra']]
            action = [word for word in parts if word in ['clicca']]
            if direction:
                deplacer_souris(direction[0], action[0] if action else '')
