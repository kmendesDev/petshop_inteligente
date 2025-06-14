# email_utils.py
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()  # lê o arquivo .env

EMAIL_REMETENTE = st.secrets["EMAIL"]["REMETENTE"]
SENHA_REMETENTE = st.secrets["EMAIL"]["SENHA"]

  

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

def enviar_email_confirmacao_agendamento(email, nome, servico, data, hora):
    corpo = f"""
    Olá {nome},

    Seu agendamento para o serviço '{servico}' foi confirmado para o dia {data} às {hora}.

    Agradecemos por escolher o nosso Pet Shop! 🐾
    """
    msg = MIMEText(corpo)
    msg['Subject'] = "Confirmação de Agendamento - Pet Shop"
    msg['From'] = "seu_email@gmail.com"
    msg['To'] = email

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_REMETENTE, SENHA_REMETENTE)
        smtp.send_message(msg)
