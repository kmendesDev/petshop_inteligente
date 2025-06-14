# email_utils.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()  # lê o arquivo .env

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
SENHA_REMETENTE = os.getenv("SENHA_REMETENTE")
  

def enviar_email_promocional(destinatario, nome_cliente, nome_pet=None):
    assunto = "🎉 Promoção Especial de Aniversário!"
    corpo = f"""
    <h3>Olá, {nome_cliente}!</h3>
    <p>Estamos muito felizes em celebrar o aniversário {'do seu pet ' + nome_pet if nome_pet else 'com você'}!</p>
    <p>Como presente, oferecemos <strong>20% de desconto</strong> no pacote de banho nesta semana!</p>
    <p>Venha nos visitar e aproveite essa oferta especial. 🐶🐱</p>
    <p><em>Com carinho, Equipe do Pet Shop</em></p>
    """

    mensagem = MIMEMultipart()
    mensagem["From"] = EMAIL_REMETENTE
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.attach(MIMEText(corpo, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, SENHA_REMETENTE)
            servidor.sendmail(EMAIL_REMETENTE, destinatario, mensagem.as_string())
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
