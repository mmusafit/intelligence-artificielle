from googletrans import Translator
import wikipediaapi
import pyttsx3 as ttx
from selenium import webdriver 
import pywhatkit
import datetime
import fitz  
from transformers import GPT2LMHeadModel, GPT2Tokenizer, CamembertModel, CamembertTokenizer
from language_tool_python import LanguageTool

# Charger le modèle GPT-2 et le tokenizer
gpt2_model_name = "gpt2"
gpt2_model = GPT2LMHeadModel.from_pretrained(gpt2_model_name)
gpt2_tokenizer = GPT2Tokenizer.from_pretrained(gpt2_model_name)

# Charger le modèle Camembert et le tokenizer spécifique pour la langue française
camembert_model_name = "camembert-base"
camembert_model = CamembertModel.from_pretrained(camembert_model_name, is_decoder=True)
camembert_tokenizer = CamembertTokenizer.from_pretrained(camembert_model_name)

# Initialiser le moteur de synthèse vocale
engine = ttx.init()

# Configurer la voix française
engine.setProperty('voice', "french")

# Ajuster le taux de parole (rate) et le volume
engine.setProperty('rate', 150)  # Ajuste la vitesse de la parole (peut être modifié)
engine.setProperty('volume', 1.0)  # Ajuste le volume (peut être modifié)

def analyse_fichier(nom_fichier):
    with open(nom_fichier) as file:
        contenu_fichier = file.read()      
    return contenu_fichier

def obtenir_riassunto(search_query, lingua_destinazione='it'):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    wiki_wiki = wikipediaapi.Wikipedia('it', headers=headers)
    page = wiki_wiki.page(search_query)

    if not page.exists():
        return f"La page pour '{search_query}' n'existe pas sur Wikipedia."

    resume = page.summary
    translator = Translator()
    traduction = translator.translate(resume, dest=lingua_destinazione)

    return traduction.text

def generer_texte_gpt2(prompt, model, tokenizer, max_length=50, num_return_sequences=1):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(
        input_ids,
        max_length=max_length,
        num_return_sequences=num_return_sequences,
        no_repeat_ngram_size=2,
        top_k=50,
        top_p=0.95,
        temperature=0.7,
    )
    texte_genere = tokenizer.decode(output[0], skip_special_tokens=True)
    return texte_genere

def generer_texte_camembert(prompt, model, tokenizer, max_length=50, num_return_sequences=1):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(
        input_ids,
        max_length=max_length,
        num_return_sequences=num_return_sequences,
        no_repeat_ngram_size=2,
        top_k=50,
        top_p=0.95,
        temperature=0.7,
    )
    texte_genere = tokenizer.decode(output[0], skip_special_tokens=True)
    return texte_genere

def ouvrir_fichier(file_path):
    os.startfile(file_path)
    if file_path.lower().endswith(".pdf"):
        engine.say("Lecture du fichier PDF en cours...")
        engine.runAndWait()
        with fitz.open(file_path) as pdf_document:
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                text = page.get_text("text")
                engine.say(text)
                engine.runAndWait()
        engine.say("Lecture du fichier PDF terminée.")
        engine.runAndWait()
    else:
        engine.say("Le fichier n'est pas un fichier PDF alors je suis obligé d'ouvrir le fichier qui n'est pas un PDF.")
        engine.runAndWait()
        os.startfile(file_path)

def detecter_et_corriger_erreurs(texte):
    tool = LanguageTool('fr')
    corrected_text = tool.correct(texte)
    
    print("Texte original :")
    print(texte)
    print("Texte corrigé :")
    print(corrected_text)
    
    if corrected_text != texte:
        engine.say("Correction grammaticale en cours...")
        engine.runAndWait()
        engine.say(corrected_text)
        engine.runAndWait()
        return corrected_text
    else:
        engine.say("Aucune erreur grammaticale détectée.")
        engine.runAndWait()
        return texte

def enregistrer_pdf_corrigé(file_path, texte):
    with open(file_path.replace(".pdf", "_corrigé.pdf"), "w", encoding="utf-8") as f:
        f.write(texte)

def ouvrir_chrome(url):
    engine.say("Bonjour, j'ouvre la page en question.")
    engine.say("J'ai trouvé la page, maintenant je vais l'ouvrir.") 
    engine.runAndWait() 
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    driver = webdriver.Chrome(options=options)   
    driver.get(url)   
    input("Appuyez sur Entrée pour fermer le navigateur...")    
    engine.say("Page ouverte avec succès.")
    engine.runAndWait()  
    driver.quit()

def lancer_assistant():
    search_query = input("Que voulez-vous chercher sur Google ou quoi d'autre puis-je faire pour vous? ")
    engine.say(search_query)
    engine.runAndWait()

    if "youtube" in search_query:
        video = input("Quelle musique ou vidéo YouTube voulez-vous écouter?")
        engine.say(video)
        engine.runAndWait()
        print(video)       
        pywhatkit.playonyt(video)

    elif "heure" in search_query:
        heure_actuelle = datetime.datetime.now().strftime("%H:%M")
        print("Il est ", heure_actuelle)
        engine.say(heure_actuelle)
        engine.runAndWait()
    elif "jour et année" in search_query:
        date_actuelle = datetime.datetime.now().strftime("Il est %A %d/%m/%Y")
        engine.say(date_actuelle)
        engine.runAndWait()

    elif "lire fichier " in search_query:
        nom_fichier = input("Quel fichier voulez-vous lire en ce moment? ")
        engine.say(nom_fichier)
        engine.runAndWait()
        contenu_fichier = analyse_fichier(nom_fichier)
        engine.say(contenu_fichier)
        engine.runAndWait()
        engine.say("J'ai fini de lire le document.")
        engine.runAndWait()
    elif "dialogue" in search_query:
        prompt = input("Veuillez saisir votre prompt pour le dialogue avec l'assistant : ")
        texte_genere = generer_texte_gpt2(prompt, gpt2_model, gpt2_tokenizer)
        engine.say(texte_genere)
        engine.runAndWait()
    elif "wikipedia" in search_query:
        search_query = input("Que voulez-vous rechercher sur Wikipedia? ")
        lingua_destinazione = input("Dans quelle langue souhaitez-vous le résumé? (par exemple 'it' pour l'italien): ")
        riassunto_tradotto = obtenir_riassunto(search_query, lingua_destinazione)
        engine.say(riassunto_tradotto)
        engine.runAndWait()
        print(riassunto_tradotto)
    elif "stackoverflow" in search_query:
        search_query = input("Que voulez-vous rechercher sur StackOverflow? ")
        url = f"https://stackoverflow.com/search?q={search_query}"
        ouvrir_chrome(url)
    elif "github" in search_query:
        search_query = input("Que voulez-vous rechercher sur GitHub? ")
        url = f"https://github.com/search?q={search_query}"
        ouvrir_chrome(url)
    elif "ouvrir le fichier" in search_query:
        file_path = input("Quel fichier voulez-vous ouvrir? ").strip()
        engine.say(file_path)
        engine.runAndWait()
        ouvrir_fichier(file_path)
    elif "correction pdf" in search_query:
        file_path = input("Quel fichier PDF voulez-vous corriger? ").strip()
        engine.say(file_path)
        engine.runAndWait()
        with fitz.open(file_path) as pdf_document:
            texte_pdf = ""
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                texte_pdf += page.get_text("text")

        texte_corrigé = detecter_et_corriger_erreurs(texte_pdf)

        # Utiliser le modèle Camembert pour compléter le texte
        texte_complet = generer_texte_camembert(texte_corrigé, camembert_model, camembert_tokenizer)

        enregistrer_pdf_corrigé(file_path, texte_complet)

        engine.say("Correction et complétion du fichier PDF terminées.")
        engine.runAndWait()

    else:
        url = f"https://www.{search_query}.com/"    
        ouvrir_chrome(url)

while True:
    text = input("Cliquez sur 'no stop' pour effectuer la recherche ou 'stop' pour arrêter: ")
    if text.lower() == "stop":
        engine.say("Au revoir!")
        engine.runAndWait() 
        break
    elif "no stop" in text.lower():
        engine.say("Bonjour, je suis votre fidèle assistante vocale prête à vous aider avec plaisir.")
        engine.runAndWait() 
        lancer_assistant()
