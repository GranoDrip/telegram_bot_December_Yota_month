# Usa un'immagine Python leggera come base
FROM python:3.10-slim

# Imposta la cartella di lavoro dentro il container
WORKDIR /app

# Copia il file dei requisiti e installa le librerie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice (il tuo bot.py)
COPY bot.py .

# Comando per avviare il bot quando parte il container
CMD ["python", "bot.py"]
