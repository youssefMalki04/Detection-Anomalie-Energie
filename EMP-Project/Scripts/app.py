import streamlit as st
st.set_page_config(page_title="Analyse EMP multi-marchés", layout="wide")

import pandas as pd
import requests
from io import BytesIO
from streamlit_autorefresh import st_autorefresh
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

st_autorefresh(interval=3600000, key="auto-refresh")

st.title("📡 Analyse automatique des données EMP - Multi Marchés")

# ✅ Liste complète des marchés avec leurs URLs
urls = {
    "TEST Singapore spot forward POWER": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/3423",
    "TEST Australia spot forward POWER": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/3420",
    "AUSTRALIA SPOT FORWARD POWER": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/4964",
    "TEST Japan spot forward POWER": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/3422",
    "TEST spot forward METAL": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/3421",
    "Spot Forward Metals": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/5125",
    "THE markets": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/4206",
    "Spain Daniela": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/2427",
    "Romania Daniela": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/2426",
    "Poland Daniela": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/2931",
    "Germany Daniela": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/2425",
    "Hungary": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/2436",
    "Turkey": "https://www.energymarketprice.com/hedgesnew/server/api/statistictable/2444"
}

def send_email_anomalies(all_anomalies):
    sender = "youssef4.malki@gmail.com"
    receiver = "youssef4.malki@gmail.com"
    password = "igjo sjaq bowk cttn"

    # Créer le message email
    email_msg = MIMEMultipart("alternative")
    email_msg['Subject'] = "⚠️ Anomalies détectées - EMP Multi Marchés"
    email_msg['From'] = sender
    email_msg['To'] = receiver

    corps_html = """
    <html><body>
    <p>Bonjour,</p>
    <p>Voici les anomalies détectées aujourd'hui dans les données EMP :</p>
    """
    total = 0
    for marché, messages in all_anomalies.items():
        if messages:
            corps_html += f"<h3>{marché}</h3><ul>"
            for anomaly_msg in messages:  # Renommé pour éviter la confusion
                parts = anomaly_msg[2:].split(" : ", 1)
                if len(parts) == 2:
                    market, detail = parts
                    corps_html += f"<li>🔸 <b>{market}</b> : {detail}</li>"
                else:
                    corps_html += f"<li>{anomaly_msg}</li>"
            corps_html += "</ul>"
            total += len(messages)

    corps_html += f"""
    <p><b>Total :</b> {total} anomalies détectées.</p>
    <p>Cordialement,<br>Bot EMP</p></body></html>
    """

    # Attacher le contenu HTML
    email_msg.attach(MIMEText(corps_html, 'html', 'utf-8'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(email_msg)
        st.success("📤 Email envoyé avec succès.")
    except Exception as e:
        st.error(f"Erreur d'envoi d'email : {e}")

# Initialisation des variables
all_anomalies = {}
titres_a_exclure = ["Electricity", "Gas", "Coal", "CO2", "Oil"]

# Traitement de chaque marché
for marché, url in urls.items():
    try:
        st.info(f"🔍 Traitement : {marché}")
        response = requests.get(url)
        response.raise_for_status()

        df = pd.read_excel(BytesIO(response.content))
        df.replace(["-", "", " "], pd.NA, inplace=True)
        df = df.set_index(df.columns[0])
        df = df[~df.index.isin(titres_a_exclure)]

        messages = []
        for market_name, row in df.iterrows():
            for date_str, value in row.items():
                try:
                    date_obj = pd.to_datetime(date_str)
                    jour = date_obj.strftime("%A")
                    date_fmt = f"{date_obj.day}/{date_obj.month} ({jour})"
                except:
                    date_fmt = str(date_str)

                if pd.isna(value):
                    messages.append(f"🔸 {market_name} : valeur manquante le {date_fmt}")
                elif value == 0:
                    messages.append(f"🔸 {market_name} : valeur nulle (0) le {date_fmt}")

        all_anomalies[marché] = messages

        if messages:
            st.warning(f"{len(messages)} anomalies détectées pour {marché}")
            for anomaly_msg in messages:
                st.markdown(f"<p>{anomaly_msg}</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Erreur pour {marché} : {e}")

# 📧 Envoi du mail global
if any(all_anomalies.values()):
    send_email_anomalies(all_anomalies)