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

# ✅ COMANDO REGISTRO ORGANIZZAZIONE

CANALE_RICHIESTE_ID = 1368676791094612028
THUMBNAIL_URL = "https://media.discordapp.net/attachments/1305532702560092211/1305537542388453446/ca921a39b77c3f617eae15daae4805d5.png?ex=6860a2d5&is=685f5155&hm=603aaf0917d163cd9bcf73459fc243c3c60eb2b295c224dd703d9c91f950ab44&=&format=webp&quality=lossless&width=848&height=848"

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
        embed.add_field(name="Nome Roblox", value=self.nome_roblox.value, inline=False)
        embed.add_field(name="Nome Discord", value=self.nome_discord.value, inline=False)
        embed.add_field(name="Nome Organizzazione", value=self.nome_organizzazione.value, inline=False)
        embed.add_field(name="Tipo Organizzazione", value=self.tipo_organizzazione.value, inline=False)
        embed.add_field(name="Zona nella quale si vuole operare", value=self.zona_operativa.value, inline=False)
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
            self.embed.title = "Richiesta Organizzazione Accettata!"
            self.embed.color = discord.Color.green()
            self.embed.add_field(name="Note Aggiuntive", value=self.note.value, inline=False)
        else:
            self.embed.title = "Richiesta Organizzazione Rifiutata"
            self.embed.color = discord.Color.red()
            self.embed.add_field(name="Motivazione del Rifiuto", value=self.note.value, inline=False)

        await self.interazione_originale.message.edit(embed=self.embed, view=None)

        try:
            await self.utente.send(embed=self.embed)
        except discord.Forbidden:
            await interaction.followup.send("⚠️ Impossibile inviare un DM all'utente.", ephemeral=True)

        await interaction.response.send_message("Richiesta gestita con successo.", ephemeral=True)

@bot.tree.command(name="registro-organizzazione", description="Registra una nuova organizzazione criminale")
async def registro_organizzazioni(interaction: discord.Interaction):
    await interaction.response.send_modal(RegistroOrganizzazioneModal())

# ✅ COMANDO SEGNALAZIONE FDO

CANALE_SEGNALAZIONI_ID = 1368496866764783617
RUOLO_DA_PINGARE_ID = 1368521510272372867

THUMBNAIL_URL = "https://media.discordapp.net/attachments/1305532702560092211/1305537542388453446/ca921a39b77c3f617eae15daae4805d5.png?ex=6860a2d5&is=685f5155&hm=603aaf0917d163cd9bcf73459fc243c3c60eb2b295c224dd703d9c91f950ab44"

class NoteModal(discord.ui.Modal, title="Motivazione / Note Aggiuntive"):
    def __init__(self, user, embed, message, approvato: bool):
        super().__init__()
        self.user = user
        self.embed = embed
        self.message = message
        self.approvato = approvato

    note = discord.ui.TextInput(label="Motivazione / Note", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        if self.approvato:
            self.embed.title = "Segnalazione Accettata!"
            self.embed.color = discord.Color.green()
            self.embed.add_field(name="Note Aggiuntive", value=self.note.value, inline=False)
        else:
            self.embed.title = "Segnalazione Rifiutata"
            self.embed.color = discord.Color.red()
            self.embed.add_field(name="Motivazione del Rifiuto", value=self.note.value, inline=False)

        await self.message.edit(embed=self.embed, view=None)

        try:
            dm_embed = self.embed.copy()
            await self.user.send("📢 Esito della tua segnalazione FDO:", embed=dm_embed)
        except:
            pass

        await interaction.response.send_message("✅ Esito gestito con successo.", ephemeral=True)

class AzioneView(discord.ui.View):
    def __init__(self, user, embed):
        super().__init__(timeout=None)
        self.user = user
        self.embed = embed

    @discord.ui.button(label="Accetta", style=discord.ButtonStyle.success)
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Non hai il permesso per usare questo pulsante.", ephemeral=True)
        await interaction.response.send_modal(NoteModal(self.user, self.embed, interaction.message, True))

    @discord.ui.button(label="Rifiuta", style=discord.ButtonStyle.danger)
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Non hai il permesso per usare questo pulsante.", ephemeral=True)
        await interaction.response.send_modal(NoteModal(self.user, self.embed, interaction.message, False))

class SegnaleFDOModal(discord.ui.Modal, title="Segnalazione FDO"):
    target = discord.ui.TextInput(label="Target (utente segnalato)", required=True)
    motivazione = discord.ui.TextInput(label="Motivazione", style=discord.TextStyle.paragraph, required=True)
    prove = discord.ui.TextInput(label="Prove (link)", required=True)
    oggetti = discord.ui.TextInput(label="Oggetti da rimborsare (facoltativo)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Segnalazione FDO Inviata",
            color=discord.Color.orange()
        )
        embed.add_field(name="Target", value=self.target.value, inline=False)
        embed.add_field(name="Motivazione", value=self.motivazione.value, inline=False)
        embed.add_field(name="Prove", value=self.prove.value, inline=False)
        embed.add_field(name="Oggetti da Rimborsare", value=self.oggetti.value or "N/A", inline=False)
        embed.set_footer(text=f"ID Richiedente: {interaction.user.id}")
        embed.set_thumbnail(url=THUMBNAIL_URL)

        view = AzioneView(interaction.user, embed)
        canale = interaction.guild.get_channel(CANALE_SEGNALAZIONI_ID)
        ruolo = interaction.guild.get_role(RUOLO_DA_PINGARE_ID)

        if canale:
            await canale.send(content=ruolo.mention if ruolo else "", embed=embed, view=view)
            await interaction.response.send_message("✅ Segnalazione FDO inviata con successo!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Errore: canale delle segnalazioni non trovato.", ephemeral=True)

@bot.tree.command(name="segnala-fdo", description="Invia una segnalazione per FDO")
async def segnale_fdo(interaction: discord.Interaction):
    await interaction.response.send_modal(SegnaleFDOModal())

# ✅ COMANDO RICHIESTA TAGLIA

THUMBNAIL_URL = "https://media.discordapp.net/attachments/1305532702560092211/1305537542388453446/ca921a39b77c3f617eae15daae4805d5.png?ex=6860a2d5&is=685f5155&hm=603aaf0917d163cd9bcf73459fc243c3c60eb2b295c224dd703d9c91f950ab44"

CANALE_TAGLIA_ID = 1370048407628152892

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
    organizzazione = discord.ui.TextInput(label="Organizzazione del mittente", required=True)
    motivazione = discord.ui.TextInput(label="Motivazione", style=discord.TextStyle.paragraph, required=True)
    prove = discord.ui.TextInput(label="Prove (link, testi, ecc)", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Richiesta Taglia Inviata",
            color=discord.Color.orange()
        )
        embed.add_field(name="Nome Roblox", value=self.nome_roblox.value, inline=False)
        embed.add_field(name="Nome Discord", value=self.nome_discord.value, inline=False)
        embed.add_field(name="Organizzazione del mittente", value=self.organizzazione.value, inline=False)
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

# ✅ SISTEMA LOGS

LOG_CHANNEL_ID = 1388633244806942762  # ID del canale log

async def log_to_channel(bot: commands.Bot, message: str):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        try:
            await channel.send(f"🪵 {message}")
        except Exception:
            pass

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} è online.")
    await log_to_channel(bot, f"✅ Il bot è online come `{bot.user}` (ID: {bot.user.id})")

@bot.event
async def on_application_command(interaction: discord.Interaction):
    user = interaction.user
    await log_to_channel(bot, f"📥 Comando `{interaction.command.name}` eseguito da {user.mention} (`{user.id}`)")

@bot.event
async def on_command(ctx):
    await log_to_channel(bot, f"📥 Comando `{ctx.command}` eseguito da {ctx.author} (`{ctx.author.id}`)")

@bot.event
async def on_error(event, *args, **kwargs):
    error_trace = traceback.format_exc()
    error_trace = error_trace[:1900]  
    await log_to_channel(bot, f"❌ Errore globale in `{event}`:\n```\n{error_trace}\n```")

@bot.event
async def on_command_error(ctx, error):
    await log_to_channel(bot, f"⚠️ Errore nel comando `{ctx.command}` da `{ctx.author}`:\n`{str(error)}`")

async def log_esito(title: str, approvato: bool, moderatore: discord.User, utente: discord.User, motivazione: str):
    emoji = "✅" if approvato else "❌"
    stato = "approvata" if approvato else "rifiutata"
    motivazione = motivazione[:150]
    await log_to_channel(
        bot,
        f"{emoji} Richiesta **{title}** {stato} da `{moderatore}` per `{utente}`.\n📄 Motivazione: {motivazione}"
    )


if __name__ == "__main__":
    token = os.getenv("CRIMI_TOKEN")
    if token:
        print("[DEBUG] Avvio bot...")
        bot.run(token)
    else:
        print("[DEBUG] Variabile CRIMI_TOKEN non trovata.")
