import os
import discord
from discord.ext import commands
from discord import app_commands, ui, Interaction, TextStyle
from flask import Flask
from threading import Thread
import unicodedata

app = Flask('')

@app.route('/')
def home():
    return "Bot attivo."

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

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

# ✅ COMANDO RICHIESTE

CANALE_RICHIESTE_ID = 1397918628384342047
THUMBNAIL_URL = "https://media.discordapp.net/attachments/1344394355229720596/1397919905449377792/Logo_Corleone_3.webp?ex=688379dd&is=6882285d&hm=4d2804e37661fddfd5ed6b023adc20b785e2d04d360d80047a4d7f0336896341&=&format=webp&width=662&height=662"

class RichiestaArruolamentoModal(discord.ui.Modal, title="Richiedi Arruolamento"):
    nome_roblox = discord.ui.TextInput(label="Nome Roblox (Main)", required=True)
    nome_roblox_alt = discord.ui.TextInput(label="Nome Roblox ALT (Solo per chi Gioca da Alt)", required=False)
    attività_game = discord.ui.TextInput(label="Quanto sei attivo da 1 a 10:", required=True)
    motivazione = discord.ui.TextInput(label="Perchè vuoi entrare in questa organizzazione:", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Richiesta Arruolamento",
            color=discord.Color.red()
        )
        embed.add_field(name="Nome Roblox (Main)", value=self.nome_roblox.value, inline=False)
        embed.add_field(name="Nome Roblox ALT", value=self.nome_roblox_alt.value, inline=False)
        embed.add_field(name="Quanto sei attivo da 1 a 10:", value=self.attività_game.value, inline=False)
        embed.add_field(name="Perchè vuoi entrare in questa organizzazione:", value=self.motivazione.value, inline=False)
        embed.set_footer(text=f"ID Richiedente: {interaction.user.id}")
        embed.set_thumbnail(url=THUMBNAIL_URL)

        view = AzioneView(interaction.user, embed)
        canale = interaction.guild.get_channel(CANALE_RICHIESTE_ID)

        if canale:
            await canale.send(embed=embed, view=view)
            await interaction.response.send_message("✅ Richiesta inviata correttamente!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Errore: canale non trovato.", ephemeral=True)

class AzioneView(discord.ui.View):
    def __init__(self, utente: discord.User, embed: discord.Embed):
        super().__init__(timeout=None)
        self.utente = utente
        self.embed = embed

    @discord.ui.button(label="Accetta", style=discord.ButtonStyle.success)
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NoteModal(True, self.embed.copy(), self.utente, interaction))

    @discord.ui.button(label="Rifiuta", style=discord.ButtonStyle.danger)
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NoteModal(False, self.embed.copy(), self.utente, interaction))

class NoteModal(discord.ui.Modal, title="Note o Motivazione"):
    note = discord.ui.TextInput(label="Note o motivazione", style=discord.TextStyle.paragraph, required=True)

    def __init__(self, accettato: bool, embed: discord.Embed, utente: discord.User, interazione_originale: discord.Interaction):
        super().__init__()
        self.accettato = accettato
        self.embed = embed
        self.utente = utente
        self.interazione_originale = interazione_originale

    async def on_submit(self, interaction: discord.Interaction):
        if self.accettato:
            self.embed.title = "Richiesta Arruolamento Accettata!"
            self.embed.color = discord.Color.green()
            self.embed.add_field(name="Note Aggiuntive", value=self.note.value, inline=False)
        else:
            self.embed.title = "Richiesta Arruolamento Rifiutata"
            self.embed.color = discord.Color.red()
            self.embed.add_field(name="Motivazione del Rifiuto", value=self.note.value, inline=False)

        await self.interazione_originale.message.edit(embed=self.embed, view=None)

        try:
            await self.utente.send(embed=self.embed)
        except discord.Forbidden:
            await interaction.followup.send("⚠️ Impossibile inviare un DM all'utente.", ephemeral=True)

        await interaction.response.send_message("Richiesta gestita con successo.", ephemeral=True)

@bot.tree.command(name="richiesta-arruolamento", description="Richiedi di essere Arruolato.")
async def richiesta.arruolamento(interaction: discord.Interaction):
    await interaction.response.send_modal(RichiestaArruolamentoModal())

# ✅ COMANDO RICHIESTA TAGLIA

THUMBNAIL_URL = "https://media.discordapp.net/attachments/1344394355229720596/1397919905449377792/Logo_Corleone_3.webp?ex=688379dd&is=6882285d&hm=4d2804e37661fddfd5ed6b023adc20b785e2d04d360d80047a4d7f0336896341&=&format=webp&width=662&height=662"

CANALE_TAGLIA_ID = 1397922199209246822

class NoteTagliaModal(discord.ui.Modal, title="Motivazione / Note Aggiuntive"):
    def __init__(self, user, embed, message, approvato: bool):
        super().__init__()
        self.user = user
        self.embed = embed
        self.message = message
        self.approvato = approvato

    note = discord.ui.TextInput(label="Motivazione / Note", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        if self.approvato:
            self.embed.title = "Richiesta Taglia Accettata!"
            self.embed.color = discord.Color.green()
            self.embed.add_field(name="Note Aggiuntive", value=self.note.value, inline=False)
        else:
            self.embed.title = "Richiesta Taglia Rifiutata"
            self.embed.color = discord.Color.red()
            self.embed.add_field(name="Motivazione del Rifiuto", value=self.note.value, inline=False)

        await self.message.edit(embed=self.embed, view=None)

        try:
            dm_embed = self.embed.copy()
            await self.user.send("📢 Esito della tua richiesta taglia:", embed=dm_embed)
        except:
            pass

        await interaction.response.send_message("✅ Esito gestito con successo.", ephemeral=True)

class AzioneTagliaView(discord.ui.View):
    def __init__(self, user, embed):
        super().__init__(timeout=None)
        self.user = user
        self.embed = embed

    @discord.ui.button(label="Accetta", style=discord.ButtonStyle.success)
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Non hai il permesso per usare questo pulsante.", ephemeral=True)
        await interaction.response.send_modal(NoteTagliaModal(self.user, self.embed, interaction.message, True))

    @discord.ui.button(label="Rifiuta", style=discord.ButtonStyle.danger)
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Non hai il permesso per usare questo pulsante.", ephemeral=True)
        await interaction.response.send_modal(NoteTagliaModal(self.user, self.embed, interaction.message, False))

class RichiestaTagliaModal(discord.ui.Modal, title="Richiesta Taglia"):
    nome_roblox = discord.ui.TextInput(label="Nome Roblox", required=True)
    nome_discord = discord.ui.TextInput(label="Nome Discord", required=True)
    motivazione = discord.ui.TextInput(label="Motivazione", style=discord.TextStyle.paragraph, required=True)
    prove = discord.ui.TextInput(label="Prove (link, testi, ecc)", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Richiesta Taglia Inviata",
            color=discord.Color.orange()
        )
        embed.add_field(name="Nome Roblox", value=self.nome_roblox.value, inline=False)
        embed.add_field(name="Nome Discord", value=self.nome_discord.value, inline=False)
        embed.add_field(name="Motivazione", value=self.motivazione.value, inline=False)
        embed.add_field(name="Prove", value=self.prove.value, inline=False)
        embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=f"ID Richiedente: {interaction.user.id}")

        view = AzioneTagliaView(interaction.user, embed)

        canale = interaction.guild.get_channel(CANALE_TAGLIA_ID)
        if canale:
            await canale.send(embed=embed, view=view)
            await interaction.response.send_message("✅ Richiesta taglia inviata correttamente!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Errore: canale non trovato.", ephemeral=True)

@bot.tree.command(name="richiesta-taglia", description="Invia una richiesta di taglia")
async def richiesta_taglia(interaction: discord.Interaction):
    await interaction.response.send_modal(RichiestaTagliaModal())


if __name__ == "__main__":
    token = os.getenv("CORLEONE_TOKEN")
    if token:
        print("[DEBUG] Avvio bot...")
        bot.run(token)
    else:
        print("[DEBUG] Variabile CORLEONE_TOKEN non trovata.")
