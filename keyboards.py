from telegram import ReplyKeyboardMarkup
from config import NOMINATIVI_SPECIALI,BANDE_DATA,MODI_DATA

# Si potrebbe anche pensare di creare una KB con una sola funzione 
# Passando come parametri il max per riga e la LISTA

# Keyboard con i nominativi
def getKeyboardNominativi():
    """Genera la keyboard dei nominativi speciali, max 3 pulsanti per riga."""
    keyboard = []
    riga = []

    for c in NOMINATIVI_SPECIALI:
        riga.append(c)
        if len(riga) == 3:
            keyboard.append(riga)
            riga = []

    if riga:
        keyboard.append(riga)

    return ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        resize_keyboard=True
    )

# Keyboard con le bande
def getKeyboard_Bande():
    """Genera la keyboard delle bande, max 4 pulsanti per riga."""
    keyboard = []
    riga = []

    for b in BANDE_DATA:
        riga.append(b)
        if len(riga) == 4:
            keyboard.append(riga)
            riga = []

    if riga:
        keyboard.append(riga)

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

# Keyboard con le modalità di trasimissione
def getKeyboard_Modi():
    """Genera la keyboard dei modi, max 4 pulsanti per riga."""
    keyboard = []
    riga = []

    for m in MODI_DATA:
        riga.append(m)
        if len(riga) == 4:
            keyboard.append(riga)
            riga = []

    if riga:
        keyboard.append(riga)

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )