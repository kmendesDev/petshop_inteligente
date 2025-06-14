import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, date
from email_utils import enviar_email_promocional, enviar_email_confirmacao_agendamento 
from datetime import date

# Inicializa o Firebase
import json
cred = credentials.Certificate(dict(st.secrets["FIREBASE"]))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("🐾 Sistema Pet Shop - MVP")

aba = st.sidebar.radio("Menu Principal", [
    "Cadastrar Cliente", "Cadastrar Pet", "Listar Pets", "Agendar Serviço", 
    "Registrar Compra", "🎂 Aniversariantes de Hoje"
])

if aba == "Cadastrar Cliente":
    st.header("Cadastro de Cliente")
    with st.form("form_cliente"):
        nome = st.text_input("Nome completo")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")
        nascimento = st.date_input(
            "Data de nascimento do cliente",
            value=date(1990, 1, 1),  # valor inicial
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )
        submitted = st.form_submit_button("Salvar")

        if submitted:
            doc_ref = db.collection("clientes").document()
            doc_ref.set({
                "nome": nome,
                "email": email,
                "telefone": telefone,
                "nascimento": nascimento.strftime("%Y-%m-%d"),
                "criado_em": datetime.now()
            })
            st.success(f"Cliente '{nome}' cadastrado com sucesso!")

elif aba == "Cadastrar Pet":
    st.header("Cadastro de Pet")
    clientes = db.collection("clientes").stream()
    lista_clientes = [(cli.id, cli.to_dict()["nome"]) for cli in clientes]

    if not lista_clientes:
        st.warning("Cadastre um cliente primeiro!")
    else:
        cliente_escolhido = st.selectbox("Escolha o tutor:", lista_clientes, format_func=lambda x: x[1])

        with st.form("form_pet"):
            nome_pet = st.text_input("Nome do pet")
            especie = st.selectbox("Espécie", ["Cachorro", "Gato", "Outro"])
            raca = st.text_input("Raça")
            nascimento = st.date_input(
                "Data de nascimento do cliente",
                value=date(1990, 1, 1),  # valor inicial
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
            salvar_pet = st.form_submit_button("Salvar pet")

            if salvar_pet:
                cliente_id = cliente_escolhido[0]
                pet_ref = db.collection("clientes").document(cliente_id).collection("pets").document()
                pet_ref.set({
                    "nome": nome_pet,
                    "especie": especie,
                    "raca": raca,
                    "nascimento": nascimento.strftime("%Y-%m-%d")
                })
                st.success(f"Pet '{nome_pet}' cadastrado com sucesso para o cliente {cliente_escolhido[1]}!")

elif aba == "Listar Pets":
    st.header("Pets por Cliente")
    clientes = db.collection("clientes").stream()

    for cli in clientes:
        cliente = cli.to_dict()
        st.subheader(f"👤 {cliente['nome']} ({cliente['email']})")
        pets_ref = db.collection("clientes").document(cli.id).collection("pets").stream()
        pets = list(pets_ref)

        if not pets:
            st.write("Nenhum pet cadastrado.")
        else:
            for pet in pets:
                pet_info = pet.to_dict()
                st.markdown(f"- 🐾 **{pet_info['nome']}** | {pet_info['especie']} - {pet_info['raca']} | Nasc: {pet_info['nascimento']}")

elif aba == "Agendar Serviço":
    st.header("Agendamento de Serviços")

    # Busca clientes para selecionar
    clientes = db.collection("clientes").stream()
    lista_clientes = [(cli.id, cli.to_dict()["nome"]) for cli in clientes]

    if not lista_clientes:
        st.warning("Cadastre um cliente primeiro!")
    else:
        cliente_escolhido = st.selectbox("Escolha o cliente:", lista_clientes, format_func=lambda x: x[1])

        with st.form("form_agendamento"):
            servico = st.selectbox("Serviço", ["Banho", "Tosa", "Vacinação", "Consulta Veterinária", "Outro"])
            data = st.date_input("Data do serviço")
            hora = st.time_input("Hora do serviço")
            enviar = st.form_submit_button("Agendar")

            if enviar:
                agendamento_ref = db.collection("clientes").document(cliente_escolhido[0]).collection("agendamentos").document()
                agendamento_ref.set({
                    "servico": servico,
                    "data": data.strftime("%Y-%m-%d"),
                    "hora": hora.strftime("%H:%M"),
                    "status": "agendado",
                    "criado_em": datetime.now()
                })
                st.success(f"Serviço '{servico}' agendado para {cliente_escolhido[1]} em {data.strftime('%d/%m/%Y')} às {hora.strftime('%H:%M')}!")
                    # Buscar e-mail do cliente para confirmação
                cliente_doc = db.collection("clientes").document(cliente_escolhido[0]).get()
                cliente_info = cliente_doc.to_dict()
                email = cliente_info.get("email", "")
                nome_cliente = cliente_info.get("nome", "")

                if email:
                    try:
                        enviar_email_confirmacao_agendamento(
                            email=email,
                            nome=nome_cliente,
                            servico=servico,
                            data=data.strftime('%d/%m/%Y'),
                            hora=hora.strftime('%H:%M')
                        )
                        st.info(f"E-mail de confirmação enviado para {email}.")
                    except Exception as e:
                        st.warning(f"Erro ao enviar e-mail: {e}")



elif aba == "Registrar Compra":
    st.header("Registrar Compra do Cliente")
    clientes = db.collection("clientes").stream()
    lista_clientes = [(cli.id, cli.to_dict()["nome"]) for cli in clientes]

    if not lista_clientes:
        st.warning("Cadastre um cliente primeiro!")
    else:
        cliente_escolhido = st.selectbox("Escolha o cliente:", lista_clientes, format_func=lambda x: x[1])

        with st.form("form_compra"):
            produto = st.text_input("Produto ou serviço")
            valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            data = st.date_input(
                "Data da compra",    
                value=date.today(),  
                min_value=date.today()
                )
            salvar_compra = st.form_submit_button("Salvar compra")

            if salvar_compra:
                compra_ref = db.collection("clientes").document(cliente_escolhido[0]).collection("compras").document()
                compra_ref.set({
                    "produto": produto,
                    "valor": valor,
                    "data": data.strftime("%Y-%m-%d"),
                    "criado_em": datetime.now()
                })
                st.success(f"Compra registrada com sucesso para o cliente {cliente_escolhido[1]}!")

elif aba == "🎂 Aniversariantes de Hoje":
    st.header("🎉 Pets e Clientes Aniversariantes de Hoje")
    hoje = date.today()

    if st.button("Enviar e-mails de aniversário"):
        emails_enviados = set()
        clientes = db.collection("clientes").stream()
        enviados_count = 0

        for cli in clientes:
            cliente_id = cli.id
            cliente = cli.to_dict()
            email = cliente.get("email", "")
            nome_cliente = cliente.get("nome", "")

            # Verifica aniversário do cliente
            nascimento_cliente = cliente.get("nascimento", None)
            if nascimento_cliente:
                nasc = datetime.strptime(nascimento_cliente, "%Y-%m-%d").date()
                if nasc.month == hoje.month and nasc.day == hoje.day:
                    if email and email not in emails_enviados:
                        enviar_email_promocional(email, nome_cliente)
                        emails_enviados.add(email)
                        enviados_count += 1
                    st.success(f"E-mail enviado para o cliente {nome_cliente} 🎂")

            # Verifica aniversário de pets
            pets_ref = db.collection("clientes").document(cliente_id).collection("pets").stream()
            for pet in pets_ref:
                pet_info = pet.to_dict()
                if "nascimento" in pet_info:
                    nasc = datetime.strptime(pet_info["nascimento"], "%Y-%m-%d").date()
                    if nasc.month == hoje.month and nasc.day == hoje.day:
                        if email and email not in emails_enviados:
                            enviar_email_promocional(email, nome_cliente, pet_info['nome'])
                            emails_enviados.add(email)
                            enviados_count += 1
                        st.success(f"E-mail enviado para o pet {pet_info['nome']}, tutor {nome_cliente} 🎂")

        if enviados_count == 0:
            st.info("Nenhum aniversariante encontrado para hoje.")
        else:
            st.balloons()
            st.success(f"Total de {enviados_count} e-mails enviados.")
