import os
import telebot
from flask import Flask, request
import pandas as pd
import re

# Token du bot Telegram
TOKEN = '7937958121:AAEe9rgnyaIUOcEm0dAMOcRsXK_dvUWi81U'
bot = telebot.TeleBot(TOKEN)

# Charger le fichier Excel
excel_file = 'ecrew_list.xlsx'

# Initialiser Flask
app = Flask(__name__)

# Définir le webhook pour Telegram
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    print("Webhook received a POST request")
    json_str = request.get_data().decode('UTF-8')
    print("Received JSON: ", json_str)  # Afficher la réponse du webhook
    try:
        update = telebot.types.Update.de_json(json_str)
        print("Update parsed successfully")
        bot.process_new_updates([update])
    except Exception as e:
        print("Error parsing update:", e)
    return "OK", 200

# Commandes Telegram
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Bienvenue ! Transférez-moi un message contenant les informations de CP et/ou FO pour effectuer la recherche.")

@bot.message_handler(func=lambda message: "CP:" in message.text or "FO:" in message.text)
def find_data_from_message(message):
    try:
        # Charger les données et effectuer les recherches
        cp_match = re.search(r"CP:\s*(\d+)", message.text)
        fo_match = re.search(r"FO:\s*(\d+)", message.text)
        response = ""
        df = pd.read_excel(excel_file)

        # Vérifier et traiter la valeur CP si présente
        if cp_match:
            cp_number = int(cp_match.group(1))
            cp_result = df[df['ID'] == cp_number]
            if not cp_result.empty:
                # Formatage pour obtenir "ID ---> Nom_Prenom"
                cp_details = "\n".join([f"{row['ID']} ---> {row['Nom_Prenom']}" for _, row in cp_result.iterrows()])
                response += f"CP: {cp_details}\n"
            else:
                response += f"CP: {cp_number} not found.\n"

        # Vérifier et traiter la valeur FO si présente
        if fo_match:
            fo_number = int(fo_match.group(1))
            fo_result = df[df['ID'] == fo_number]
            if not fo_result.empty:
                # Formatage pour obtenir "ID ---> Nom_Prenom"
                fo_details = "\n".join([f"{row['ID']} ---> {row['Nom_Prenom']}" for _, row in fo_result.iterrows()])
                response += f"FO: {fo_details}\n"
            else:
                response += f"FO: {fo_number} not found."

        # Si aucune correspondance n'est trouvée et que le format n'est pas valide
        if not cp_match and not fo_match:
            response = "Format du message incorrect. Assurez-vous qu'il contient 'CP:' et/ou 'FO:'."

        # Envoyer la réponse au bot
        bot.reply_to(message, response or "Aucune donnée trouvée.")

    except Exception as e:
        bot.reply_to(message, f"Erreur : {e}")


def handle_start_help(message):
    print(f"Handling message: {message.text}")  # Afficher le message reçu

# Dans le gestionnaire de commandes Telegram
@bot.message_handler(commands=['start', 'help'])
def start_help(message):
    handle_start_help(message)
    bot.reply_to(message, "Hello! I'm your bot.")


# Configurer le webhook
def set_webhook():
    url = "https://ah-crew-id.onrender.com/7937958121:AAEe9rgnyaIUOcEm0dAMOcRsXK_dvUWi81U/"
    bot.remove_webhook()
    bot.set_webhook(url=url)
    print(f"Webhook set to {url}")
    # Vérifier l'état du webhook
    status = bot.get_webhook_info()
    print(status)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Assurez-vous que Replit utilise le port 5000
    app.run(host="0.0.0.0", port=5000)
