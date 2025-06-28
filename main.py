import os
import discord
from discord.ext import commands
from discord import app_commands, ui, Interaction, TextStyle
from flask import Flask
from threading import Thread
import unicodedata

# 🌐 Web server
app = Flask('')

@app.route('/')
def home():
    return "Bot attivo."

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# ⚙️ Setup bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        synced = await bot.tree.sync()
        print(f"[DEBUG] Comandi slash sincronizzati: {len(synced)}")
    except Exception as e:
        print(f"[DEBUG] Errore sincronizzazione: {e}")
    print(f"[DEBUG] Bot connesso come {bot.user}")

class RegistroOrganizzazioneModal(discord.ui.Modal, title="Registrazione Organizzazione"):
    nome_roblox = discord.ui.TextInput(label="Nome Roblox", required=True)
    nome_discord = discord.ui.TextInput(label="Nome Discord", required=True)
    nome_organizzazione = discord.ui.TextInput(label="Nome dell'organizzazione", required=True)
    tipo_organizzazione = discord.ui.TextInput(label="Tipo di organizzazione", required=True)
    zona_operativa = discord.ui.TextInput(label="Zona in cui vuoi operare", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Richiesta Registrazione Organizzazione",
            color=discord.Color.orange()
        )
        embed.add_field(name="👤 Nome Roblox", value=self.nome_roblox.value, inline=False)
        embed.add_field(name="💬 Nome Discord", value=self.nome_discord.value, inline=False)
        embed.add_field(name="🏢 Nome Organizzazione", value=self.nome_organizzazione.value, inline=False)
        embed.add_field(name="📦 Tipo Organizzazione", value=self.tipo_organizzazione.value, inline=False)
        embed.add_field(name="🌍 Zona Operativa", value=self.zona_operativa.value, inline=False)
        embed.set_footer(text=f"ID Richiedente: {interaction.user.id}")

        view = AzioneView(interaction.user, embed)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

class AzioneView(discord.ui.View):
    def __init__(self, utente: discord.User, embed: discord.Embed):
        super().__init__(timeout=None)
        self.utente = utente
        self.embed = embed

    @discord.ui.button(label="✅ Accetta", style=discord.ButtonStyle.success)
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NoteModal(True, self.embed, self.utente, interaction))

    @discord.ui.button(label="❌ Rifiuta", style=discord.ButtonStyle.danger)
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NoteModal(False, self.embed, self.utente, interaction))

class NoteModal(discord.ui.Modal, title="Note/Motivazione"):
    note = discord.ui.TextInput(label="Note aggiuntive o motivazione", style=discord.TextStyle.paragraph, required=True)

    def __init__(self, accettato: bool, embed: discord.Embed, utente: discord.User, interazione_originale: discord.Interaction):
        super().__init__()
        self.accettato = accettato
        self.embed = embed
        self.utente = utente
        self.interazione_originale = interazione_originale

    async def on_submit(self, interaction: discord.Interaction):
        self.embed.clear_fields()
        if self.accettato:
            self.embed.title = "✅ Richiesta Organizzazione Accettata"
            self.embed.color = discord.Color.green()
            self.embed.add_field(name="Note Aggiuntive", value=self.note.value, inline=False)
        else:
            self.embed.title = "❌ Richiesta Organizzazione Rifiutata"
            self.embed.color = discord.Color.red()
            self.embed.add_field(name="Motivazione del Rifiuto", value=self.note.value, inline=False)

        await self.interazione_originale.edit_original_response(embed=self.embed, view=None)

        try:
            await self.utente.send(embed=self.embed)
        except discord.Forbidden:
            await interaction.followup.send("⚠️ Non riesco a mandare un messaggio privato all'utente.", ephemeral=True)

        await interaction.response.send_message("Richiesta gestita correttamente.", ephemeral=True)

@bot.tree.command(name="registro-organizzazioni", description="Registra una nuova organizzazione criminale")
async def registro_organizzazioni(interaction: discord.Interaction):
    await interaction.response.send_modal(RegistroOrganizzazioneModal())

# 🚀 Avvio
if __name__ == "__main__":
    token = os.getenv("CRIMI_TOKEN")
    if token:
        print("[DEBUG] Avvio bot...")
        bot.run(token)
    else:
        print("[DEBUG] Variabile CRIMI_TOKEN non trovata.")
