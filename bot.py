import logging
import os
import requests
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# --- CONFIGURAZIONE ---
TOKEN = "xxxxxxxx"  # Inserisci qui il token del tuo bot
# Abilitiamo i log per vedere se ci sono errori nel terminale
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
YOTA_USER_TOKEN = "xxxxxxxxxx"
LOG_CHANNEL_ID = "xxxxxxx"  # Il tuo ID Telegram
LISTA_NOMINATIVI = ["xxxx","xxxxx","xxxxx", "xxxxx"] # <Nominativi speciali
LISTA_BANDE = ["80m","40m","20m","17m","15m","12m","10m","6m","2m","70cm"] # <Bande autorizzate
LISTA_MODI = ["SSB","CW","FT8","FT4","RTTY","PSK31","SSTV","FM"] # <Modi consentiti

# Stati della conversazione (serve per far capire al bot a che punto siamo)
NOMINATIVO, BANDA, MODO, SET_CALL, RICEZIONE_LOG_CHIUSURA = range(5)

# --- DATABASE IN MEMORIA (Dizionario) ---
# Struttura: { user_id_telegram: { "call": "IK0XXX", "freq": "14.200", "start_time": "..." } }
active_users = {}
user_callsigns = {} 
utenti_notifiche = set() # Insieme di chat_id che vogliono le notifiche
# --- COMANDI BASE ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Messaggio di benvenuto."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    utenti_notifiche.add(chat_id)

    await update.message.reply_text(
        f"Ciao {user.full_name}! 👋\n"
        "Sono il bot per la gestione delle attivazioni radio per il DYM 2025.\n\n"
        "Prima di iniziare a lavorare usa il comando /regole per sapere tutto sul funzinamento. \n\n"
        "Comandi disponibili:\n"
        "📜 /regole - Mostra le regole\n"
        "🔔 /notifiche - Gestisci le notifiche (in arrivo)\n"
        "🆔 /call - Aggiungi il tuo nominativo personale\n"
        "📡 /attiva - Inizia una nuova attivazione\n"
        "📝 /lista - Vedi chi è attualmente in frequenza\n"
        "🛑 /fine - Termina la tua attivazione corrente\n"
        "⚙️ /comandi - Lista dei comandi disponibili\n"
    )
    return ConversationHandler.END

# --- COMANDO /REGOLE ---
async def regole(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra le regole di utilizzo del bot."""
    await update.message.reply_text(
        "📜 Regole per l'uso del Bot di Attivazione Radio del DYM 2025 📜\n\n"
        "1. Usa il comando /call per inserire il tuo nominativo personale. (consigliato!)n"
        "2. Usa il comando /attiva per iniziare una nuova attivazione.\n"
        "3. Seleziona il tuo nominativo dalla lista proposta.\n"
        "4. Fornisci la frequenza su cui opererai.\n"
        "5. Per vedere chi è attivo, usa il comando /lista.\n"
        "6. Quando hai finito, usa il comando /fine per terminare l'attivazione e caricare i log.\n"
        "7. Usa il comando /notifiche per attivare o disattivare le notifiche (in arrivo).\n\n"
        "⚠️ Assicurati di non avere attivazioni multiple aperte contemporaneamente.\n"
        "Buon divertimento e buoni collegamenti! 📡"
    )
    await update.message.reply_text(
        f"Comandi disponibili:\n"
        "📜 /regole - Mostra le regole\n"
        "🔔 /notifiche - Gestisci le notifiche (in arrivo)\n"
        "🆔 /call - Aggiungi il tuo nominativo personale\n"
        "📡 /attiva - Inizia una nuova attivazione\n"
        "📝 /lista - Vedi chi è attualmente in frequenza\n"
        "🛑 /fine - Termina la tua attivazione corrente\n"
        "⚙️ /comandi - Lista dei comandi disponibili\n"
    )
    return ConversationHandler.END
# --- COMANDO /COMANDI ---
async def comand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mostra la lista dei comandi disponibili."""
    await update.message.reply_text(
        f"Comandi disponibili:\n"
        "📜 /regole - Mostra le regole\n"
        "🔔 /notifiche - Gestisci le notifiche (in arrivo)\n"
        "🆔 /call - Aggiungi il tuo nominativo personale\n"
        "📡 /attiva - Inizia una nuova attivazione\n"
        "📝 /lista - Vedi chi è attualmente in frequenza\n"
        "🛑 /fine - Termina la tua attivazione corrente\n"
        "⚙️ /comandi - Lista dei comandi disponibili\n"
    )
    return ConversationHandler.END

# --- Gestione delle notifiche (/notifiche) ---
async def gestisci_notifiche(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Attiva o disattiva le notifiche degli spot per l'utente."""
    chat_id = update.effective_chat.id
    
    if chat_id in utenti_notifiche:
        utenti_notifiche.remove(chat_id)
        await update.message.reply_text("🔕 Notifiche DISATTIVATE. Non riceverai più gli spot.")
    else:
        utenti_notifiche.add(chat_id)
        await update.message.reply_text("🔔 Notifiche ATTIVATE! Riceverai un messaggio ogni volta che qualcuno è ON-AIR.")

# --- GESTIONE CALL PERSONALE (/call) ---
async def imposta_call_step1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fase 1: L'utente scrive /call. Il bot chiede il nominativo."""
    await update.message.reply_text(
        "🆔 Impostazione Call Personale\n\n"
        "Per favore, scrivi ora il tuo Nominativo (es. IU3XYZ).\n"
        "Lo userò per identificarti nelle liste.",
        parse_mode="Markdown"
    )
    # Ora il bot entra in attesa di un messaggio di testo
    return SET_CALL

async def imposta_call_step2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fase 2: L'utente ha scritto il nominativo. Lo salviamo."""
    user_id = update.effective_user.id
    input_text = update.message.text.upper().strip()
    
    # Validazione base: lunghezza
    if len(input_text) < 3 or len(input_text) > 10:
        await update.message.reply_text("⚠️ Nominativo non valido (troppo corto o lungo). Riprova.")
        return SET_CALL # Rimaniamo in attesa finché non ne scrive uno giusto

    # Salviamo nel registro
    user_callsigns[user_id] = input_text
    
    await update.message.reply_text(
        f"✅ Perfetto!\n"
        f"Registrazione di {input_text} effettuata con successo.\n"
    )
    await update.message.reply_text(
        f"Comandi disponibili:\n"
        "📜 /regole - Mostra le regole\n"
        "🔔 /notifiche - Gestisci le notifiche (in arrivo)\n"
        "🆔 /call - Aggiungi il tuo nominativo personale\n"
        "📡 /attiva - Inizia una nuova attivazione\n"
        "📝 /lista - Vedi chi è attualmente in frequenza\n"
        "🛑 /fine - Termina la tua attivazione corrente\n"
        "⚙️ /comandi - Lista dei comandi disponibili\n"
    )
    return ConversationHandler.END

# --- FLUSSO "ATTIVA" (ConversationHandler) ---
async def inizia_attivazione(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fase 1: Chiede il nominativo mostrando i pulsanti."""
    user_id = update.effective_user.id
    
    if user_id in active_users:
        dati = active_users[user_id]
        await update.message.reply_text(
            f"⚠️ Risulti già attivo con il call {dati['call']}.\n"
            "Usa /fine prima di ricominciare."
        )
        return ConversationHandler.END

    # Creiamo la tastiera. Ogni pulsante è un nominativo
    keyboard = []
    riga = []
    for call in LISTA_NOMINATIVI:
        riga.append(call)
        if len(riga) == 3: # Mettiamo 3 pulsanti per riga 
            keyboard.append(riga)
            riga = []
    if riga: # Se è rimasto un pulsante spaiato, aggiungilo
        keyboard.append(riga)

    # Creiamo l'oggetto markup
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        one_time_keyboard=True,  # La tastiera sparisce dopo il click
        resize_keyboard=True     # I tasti sono piccoli e compatti
    )

    await update.message.reply_text(
        "Ok, iniziamo! 🎙️\n"
        "Seleziona il Nominativo con cui vuoi trasmettere:",
        reply_markup=reply_markup
    )
    return NOMINATIVO

def get_tastiera_bande():
    """Restituisce l'oggetto ReplyKeyboardMarkup con le bande."""
    keyboard = []
    riga = []
    for b in LISTA_BANDE:
        riga.append(b)
        if len(riga) == 4: # 4 pulsanti per riga
            keyboard.append(riga)
            riga = []
    if riga:
        keyboard.append(riga)
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
def get_tastiera_modi():
    """Restituisce l'oggetto ReplyKeyboardMarkup con i modi."""
    keyboard = []
    riga = []
    for m in LISTA_MODI:
        riga.append(m)
        if len(riga) == 4: 
            keyboard.append(riga)
            riga = []
    if riga:
        keyboard.append(riga)
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
async def ricevi_nominativo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fase 2: Salva il Call e mostra la tastiera delle Bande."""
    nominativo = update.message.text.upper().strip()
    
    # Validazione Call
    if nominativo not in LISTA_NOMINATIVI:
        # Anche qui potresti fare una funzione per la tastiera nominativi, ma per ora lasciamo così
        await update.message.reply_text(
            "⚠️ Nominativo non riconosciuto. Usa i pulsanti.",
            reply_markup=ReplyKeyboardMarkup([[c] for c in LISTA_NOMINATIVI], resize_keyboard=True)
        )
        return NOMINATIVO

    context.user_data['temp_call'] = nominativo
    
    # --- USIAMO LA NUOVA FUNZIONE QUI ---
    markup_bande = get_tastiera_bande()

    await update.message.reply_text(
        f"✅ Operi come {nominativo}.\n"
        "Ora seleziona la Banda su cui trasmetterai:",
        reply_markup=markup_bande 
    )
    
    return BANDA

async def ricevi_banda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fase 3: Riceve Banda, avvisa se ci sono altri modi attivi, ma lascia passare."""
    banda_scelta = update.message.text.strip()
    nominativo_scelto = context.user_data['temp_call']
    markup_bande = get_tastiera_bande()

    # 1. Validazione input
    if banda_scelta not in LISTA_BANDE:
        await update.message.reply_text(
            f"⚠️ Errore: '{banda_scelta}' non valida.\n👇 Usa i pulsanti:",
            reply_markup=markup_bande
        )
        return BANDA 

    # 2. CONTROLLO "SOFT" (Solo informativo)
    # Vediamo se c'è già qualcuno su questa banda con questo call per avvisare l'utente
    utenti_concorrenti = []
    for uid, dati in active_users.items():
        if dati['call'] == nominativo_scelto and dati['banda'] == banda_scelta:
            modo_usato = dati.get('modo', '???')
            op_name = dati.get('operator', 'Sconosciuto')
            utenti_concorrenti.append(f"- {modo_usato} ({op_name})")

    # Costruiamo il messaggio di risposta
    messaggio_avviso = ""
    if utenti_concorrenti:
        lista_occupati = "\n".join(utenti_concorrenti)
        messaggio_avviso = (
            f"⚠️ Nota: Su {banda_scelta} sono già attivi:\n{lista_occupati}\n"
            "Puoi operare, ma scegli un modo diverso!\n\n"
        )

    # 3. Procediamo SEMPRE verso il modo (non blocchiamo più qui)
    context.user_data['temp_banda'] = banda_scelta
    
    await update.message.reply_text(
        f"{messaggio_avviso}"
        f"👍 Banda {banda_scelta} selezionata.\n"
        "Ora seleziona il Modo di Emissione:",
        reply_markup=get_tastiera_modi()
    )
    
    return MODO
async def ricevi_modo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fase 4: Riceve Modo, controlla conflitti ESATTI e salva."""
    modo_scelto = update.message.text.strip()
    user_id = update.effective_user.id
    markup_modi = get_tastiera_modi()
    chat_id = update.effective_chat.id

    # Recuperiamo i dati temporanei
    nominativo = context.user_data['temp_call']
    banda = context.user_data['temp_banda']
    
    # 1. Validazione Modo
    if modo_scelto not in LISTA_MODI:
         await update.message.reply_text(
             "⚠️ Modo non valido! Usa i pulsanti:",
             reply_markup=markup_modi
         )
         return MODO

    # 2. CONTROLLO CONFLITTI (Call + Banda + Modo)
    # Qui il blocco è RIGIDO. Non possono esistere due stazioni uguali.
    for uid, dati in active_users.items():
        if (dati['call'] == nominativo and 
            dati['banda'] == banda and 
            dati['modo'] == modo_scelto):
            
            op_name = dati.get('operator', 'Sconosciuto')
            
            await update.message.reply_text(
                f"🛑 STOP! FREQUENZA OCCUPATA 🛑\n\n"
                f"Non puoi andare in {modo_scelto} su {banda}!\n"
                f"C'è già l'operatore: {op_name}\n\n"
                "👇 Scegli un altro modo:",
                reply_markup=markup_modi # Ridiamo i tasti dei modi
            )
            return MODO # Rimaniamo qui finché non cambia modo

    # 3. Se siamo qui, la combinazione è libera -> Salviamo!
    nome_operatore = user_callsigns.get(user_id, update.effective_user.first_name)
    ora_inizio = datetime.now().strftime("%H:%M")
    
    active_users[user_id] = {
        "call": nominativo,
        "banda": banda,
        "modo": modo_scelto,
        "freq": banda, 
        "start_time": ora_inizio,
        "operator": nome_operatore
    }
    
    await update.message.reply_text(
        f"✅ Attivazione Avviata!\n\n"
        f"🆔 Call: {nominativo}\n"
        f"〰️ Banda: {banda}\n"
        f"🔊 Modo: {modo_scelto}\n"
        f"👤 Op: {nome_operatore}\n"
        f"🕒 Ora: {ora_inizio}\n\n"
        "Buon DX! /fine per chiudere.",
        reply_markup=ReplyKeyboardRemove()
    )
    # --- 4. BROADCAST: INVIO MESSAGGIO A TUTTI GLI ISCRITTI ---
    messaggio_spot = (
        f"📡 NUOVA ATTIVAZIONE!\n\n"
        f"🗣️ {nominativo} è ON-AIR\n"
        f"〰️ {banda} | {modo_scelto}\n"
        f"👤 Op: {nome_operatore}\n"
        f"🕒 {ora_inizio}"
    )

    # Convertiamo il set in lista per evitare errori mentre cicliamo
    destinatari = list(utenti_notifiche)
    count_invii = 0

    for chat_id_destinatario in destinatari:
        # Non mandiamo la notifica a chi sta attivando (è inutile)
        if chat_id_destinatario == user_id:
            continue

        try:
            await context.bot.send_message(
                chat_id=chat_id_destinatario,
                text=messaggio_spot,
                parse_mode="Markdown"
            )
            count_invii += 1
        except Exception as e:
            # Se un utente ha bloccato il bot, lo rimuoviamo dalla lista
            # così la prossima volta non ci riproviamo e non generiamo errori
            utenti_notifiche.discard(chat_id_destinatario)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Permette di annullare l'operazione se l'utente cambia idea."""
    await update.message.reply_text("Operazione annullata.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- COMANDI DI GESTIONE ---

async def lista_attivi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra la lista formattata (Versione Sicura)."""
    if not active_users:
        await update.message.reply_text("🔇 Al momento non c'è nessuno in frequenza.")
        return

    messaggio = "📡 STAZIONI ATTIVE ORA 📡\n\n"
    
    for user_id, dati in active_users.items():
        # --- MODIFICA DI SICUREZZA ---
        # Usiamo .get() invece delle parentesi quadre dirette.
        # Se per qualche motivo manca il campo 'operator', userà '???' invece di dare errore.
        call_stazione = dati.get('call', 'Sconosciuto')
        operatore = dati.get('operator', update.effective_user.first_name) 
        banda = dati.get('banda', '???')
        modo = dati.get('modo', '')
        ora = dati.get('start_time', '??:??')
        
        messaggio += (
            f"🗣️ <b>{call_stazione}</b> (Op. {operatore})\n"
            f"〰️ Banda: {banda} \n"
            f"🔊 Modo: {modo}\n"
            f"🕒 Dalle: {ora}\n"
            f"------------------\n"
        )
    
    try:
        await update.message.reply_text(messaggio, parse_mode="HTML")
    except Exception as e:
        # Se c'è ancora un errore, lo vediamo nei log ma il bot ti avvisa
        print(f"ERRORE INVIO LISTA: {e}")
        await update.message.reply_text("⚠️ C'è stato un errore nel generare la lista. Controlla i log.")

async def fine_attivazione(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fase 1 Chiusura: Chiede il file ADIF."""
    user_id = update.effective_user.id
    
    # 1. Controllo: L'utente sta lavorando?
    if user_id not in active_users:
        await update.message.reply_text("Non risulti attivo, quindi non c'è nulla da chiudere.")
        return ConversationHandler.END

    dati = active_users[user_id]
    
    # Creiamo un tasto per chiudere senza log (in caso di emergenza)
    tasto_skip = ReplyKeyboardMarkup([["Chiudi senza Log"]], resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        f"🛑 Richiesta di Chiusura per {dati['call']}\n\n"
        "Per terminare l'attività e liberare la frequenza, **devi caricare il log**.\n"
        "📂 Invia ora il file .ADI o .ADIF qui in chat.",
        reply_markup=tasto_skip,
        parse_mode="Markdown"
    )
    
    # Passiamo allo stato di ricezione file
    return RICEZIONE_LOG_CHIUSURA

async def ricevi_log_e_chiudi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fase 2 Chiusura: Riceve file, carica su API (con allarme errore) e cancella utente."""
    user_id = update.effective_user.id
    msg_text = update.message.text 
    
    # Recuperiamo i dati dell'attivazione
    if user_id not in active_users:
        await update.message.reply_text("Errore: sessione non trovata.")
        return ConversationHandler.END
        
    dati_sessione = active_users[user_id]
    call_stazione = dati_sessione['call']
    nome_operatore = dati_sessione['operator']

    # --- CASO 1: CHIUSURA SENZA LOG ---
    if msg_text == "Chiudi senza Log":
        del active_users[user_id]
        await update.message.reply_text(
            f"⚠️ Attività chiusa SENZA caricare il log.\nRicordati di caricarlo a mano!",
            reply_markup=ReplyKeyboardRemove()
        )
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID, 
            text=f"⚠️ AVVISO: {nome_operatore} ha chiuso {call_stazione} SENZA inviare il log."
        )
        return ConversationHandler.END

    # --- CASO 2: RICEZIONE FILE ---
    document = update.message.document
    if not document:
        await update.message.reply_text("Devi inviare un file o premere 'Chiudi senza Log'.")
        return RICEZIONE_LOG_CHIUSURA

    file_name = document.file_name
    if not (file_name.lower().endswith('.adi') or file_name.lower().endswith('.adif')):
        await update.message.reply_text("⚠️ Il file deve essere .adi o .adif!")
        return RICEZIONE_LOG_CHIUSURA

    await update.message.reply_text("⏳ File ricevuto. Elaborazione e chiusura...")

    # Scarichiamo il file
    file_obj = await document.get_file()
    path_locale = f"{file_name}"
    await file_obj.download_to_drive(path_locale)

    # --- INIZIO BLOCCO TRY PRINCIPALE (Questo era quello rimasto aperto!) ---
    try:
        # A. Backup Admin
        try:
            await context.bot.send_document(
                chat_id=LOG_CHANNEL_ID,
                document=open(path_locale, 'rb'),
                caption=f"📝 Log Backup\nCall: {call_stazione}\nOp: {nome_operatore}",
                disable_notification=True
            )
        except Exception as e:
            print(f"Errore backup canale: {e}")

        if call_stazione in LISTA_NOMINATIVI:
            
            # Trasformiamo il call in minuscolo per l'URL (es. ii9yota)
            call_slug = call_stazione.lower()
            url = f"https://events.ham-yota.com/api/stations/{call_slug}/adif/upload" 
            
            headers = {"Authorization": f"Bearer {YOTA_USER_TOKEN}"} 
            
            with open(path_locale, 'rb') as f:
                response = requests.post(url, headers=headers, files={'file': f}) 
            # Lettura risposta JSON
            try:
                dati_risposta = response.json()
            except:
                dati_risposta = {}

            logging.info(f"YOTA API REPLY: Code={response.status_code} Body={response.text}")

            # CONTROLLO SUCCESSO (Status 200 E messaggio success)
            if response.status_code == 200 and dati_risposta.get('status') == 'success':
                esito_api = "✅ Upload YOTA OK"
            else:
                # Gestione Errore
                messaggio_errore = dati_risposta.get('message')
                if not messaggio_errore:
                    messaggio_errore = dati_risposta.get('status')
                if not messaggio_errore:
                    messaggio_errore = response.text

                esito_api = f"❌ Errore YOTA: {messaggio_errore}"
                
                # Allarme Telegram
                await context.bot.send_message(
                    chat_id=LOG_CHANNEL_ID,
                    text=(
                        f"🚨 ALLARME UPLOAD API 🚨\n\n"
                        f"L'operatore {nome_operatore} ha fallito l'upload per {call_stazione}.\n"
                        f"🔢 Codice HTTP: {response.status_code}\n"
                        f"📄 Motivo: `{messaggio_errore}`\n\n"
                        f"⚠️ File ADIF inviato sopra."
                    ),
                    parse_mode="Markdown"
                )

        # C. Chiusura Effettiva
        del active_users[user_id]
        
        await update.message.reply_text(
            f"🏁 ATTIVITÀ TERMINATA\n\n"
            f"Nominativo: {call_stazione}\n"
            f"Stato Log: {esito_api}\n"
            "In caso di errore rivolgiti a ... per risolvere il problema o se riesci carica il log in autonomia\n"
            "Grazie e 73! 👋",
            reply_markup=ReplyKeyboardRemove()
        )

    
    except Exception as e:
        await update.message.reply_text(f"Errore critico: {e}")
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"☠️ CRASH BOT durante chiusura di {nome_operatore}.\nErrore: {e}"
        )
        if user_id in active_users: 
            del active_users[user_id]
            
    finally:
        if os.path.exists(path_locale):
            os.remove(path_locale)

    return ConversationHandler.END
# --- MAIN ---

def main() -> None:
    """Avvia il bot."""
    # Crea l'applicazione
    application = Application.builder().token(TOKEN).build()
    # Gestore della conversazione per /attiva
    # Questo gestisce il flusso: Comando -> Chiedi Call -> Chiedi Freq -> Fine
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("attiva", inizia_attivazione)],
        states={
            NOMINATIVO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_nominativo)],
            BANDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_banda)],
            MODO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_modo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    # Gestore conversazione per /call
    conv_call = ConversationHandler(
        entry_points=[CommandHandler("call", imposta_call_step1)],
        states={
            SET_CALL: [MessageHandler(filters.TEXT & ~filters.COMMAND, imposta_call_step2)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    # Gestore per la chiusura con log
    conv_fine = ConversationHandler(
        entry_points=[CommandHandler("fine", fine_attivazione)],
        states={
            RICEZIONE_LOG_CHIUSURA: [
                MessageHandler(filters.Document.ALL, ricevi_log_e_chiudi),
                MessageHandler(filters.Regex("^Chiudi senza Log$"), ricevi_log_e_chiudi)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_fine)


    application.add_handler(conv_call)

    # Aggiunta degli handler all'applicazione
    application.add_handler(CommandHandler("regole", regole))
    application.add_handler(CommandHandler("comandi", comand))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("lista", lista_attivi))
    application.add_handler(CommandHandler("notifiche", gestisci_notifiche))
    application.add_handler(conv_handler)

    # Avvio del bot
    print("Bot in avvio...")
    application.run_polling()

if __name__ == "__main__":
    main()