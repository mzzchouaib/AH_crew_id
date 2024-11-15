import os
import telebot
import pandas as pd
import re
from flask import Flask

# Crée une application Flask pour que Render puisse détecter le port ouvert
app = Flask(__name__)

# Remplacez par le token de votre bot Telegram
TOKEN = '7937958121:AAEe9rgnyaIUOcEm0dAMOcRsXK_dvUWi81U'
bot = telebot.TeleBot(TOKEN)

# Charger le fichier Excel
excel_file = 'ecrew_list.xlsx'

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Bienvenue ! Transférez-moi un message contenant les informations de CP et/ou FO pour effectuer la recherche."
    )

@bot.message_handler(func=lambda message: "CP:" in message.text or "FO:" in message.text)
def find_data_from_message(message):
    try:
        # Message de débogage pour confirmer que la fonction est appelée
        print("Fonction de recherche appelée")

        # Extraire les valeurs après "CP:" et "FO:" dans le message
        cp_match = re.search(r"CP:\s*(\d+)", message.text)
        fo_match = re.search(r"FO:\s*(\d+)", message.text)

        # Initialiser la réponse
        response = ""

        # Charger le fichier Excel
        df = pd.read_excel(excel_file)
        print("Fichier Excel chargé")  # Message de débogage

        # Vérifier et traiter la valeur CP si présente
        if cp_match:
            cp_number = int(cp_match.group(1))
            cp_result = df[df['ID'] == cp_number]
            if not cp_result.empty:
                cp_details = " --> ".join([
                    str(row[col]) for _, row in cp_result.iterrows()
                    for col in df.columns
                ])
                response += f"CDB {cp_details}\n"
                print(f"Résultat pour CP: {response}")  # Message de débogage
            else:
                response += f"CDB {cp_number} not found.\n"
                print("CDB not found")  # Message de débogage

        # Vérifier et traiter la valeur FO si présente
        if fo_match:
            fo_number = int(fo_match.group(1))
            fo_result = df[df['ID'] == fo_number]
            if not fo_result.empty:
                fo_details = " --> ".join([
                    str(row[col]) for _, row in fo_result.iterrows()
                    for col in df.columns
                ])
                response += f"FO  {fo_details}\n"
                print(f"Résultat pour FO: {response}")  # Message de débogage
            else:
                response += f"CDB {fo_number} not found."
                print("FO not found")  # Message de débogage

        # Si aucune correspondance n'est trouvée et que le format n'est pas valide
        if not cp_match and not fo_match:
            response = "Format du message incorrect. Assurez-vous qu'il contient 'CP:' et/ou 'FO:'."
            print(response)  # Message de débogage

    except Exception as e:
        response = f"Erreur lors de la recherche : {e}"
        print(response)  # Message de débogage

    # Envoyer la réponse au bot
    bot.reply_to(message, response)
    print("Réponse envoyée")  # Message de débogage

# Démarrer le bot avec long polling
if __name__ == "__main__":
    print("Le bot est en cours d'exécution...")
    bot.polling(none_stop=True)

    # Faire tourner Flask pour répondre aux requêtes de Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
