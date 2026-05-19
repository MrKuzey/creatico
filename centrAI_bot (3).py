import discord
from discord.ext import commands
from discord import ui
from groq import Groq
import os
import random
import json

# ── Config ──────────────────────────────────────────────────────────────────
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "MTUwNDk0NTM0NTU2ODgzMzYxNw.GaSyPD.ZopoIj9bdDbc1Ve1FVmEHH6syUGWotaSU9bUic")
GROQ_API_KEY  = os.environ.get("GROQ_API_KEY",  "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")
MODEL         = "groq/compound-mini"
TRIGGER       = "!centrAI"
MAX_HISTORY   = 10
CONFIG_FILE   = "config.json"
# ────────────────────────────────────────────────────────────────────────────

groq_client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!centra_", intents=intents, help_command=None)

history: dict[int, list[dict]] = {}

# ── Config yardımcıları ───────────────────────────────────────────────────────

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_report_channel(guild_id: int) -> int | None:
    cfg = load_config()
    return cfg.get(str(guild_id))

def set_report_channel(guild_id: int, channel_id: int):
    cfg = load_config()
    cfg[str(guild_id)] = channel_id
    save_config(cfg)

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Sen CentrAI'sin — Centra adlı bir Minecraft tier testing sunucusunun "
        "resmi yapay zeka asistanısın. Görevin oyuncuların tier listesi konularında "
        "yardımcı olmak: kit değerlendirmesi, PvP mekaniklerini analiz etmek, "
        "Minecraft HCF/UHC/KitPvP meta bilgisi vermek ve oyuncuları doğru tier'a "
        "yerleştirmek için tavsiye sunmak. "
        "Türkçe ve İngilizce konuşabilirsin; kullanıcı hangi dilde yazarsa o dilde cevap ver. "
        "Kısa, net ve oyuncu dostu cevaplar ver. Discord mesaj limitine (1900 karakter) dikkat et. "
        "Eğer bir konu Minecraft tier testing ile alakalıysa detaylı ol; "
        "alakasız konularda kibarca konuyu yönlendir."
    ),
}

KIT_MODES = [
    "HCF (Hardcore Factions)", "UHC (Ultra Hardcore)", "KitPvP",
    "Crystal PvP", "Sword PvP", "Axe PvP", "Pot PvP",
    "SMP PvP", "Bridge (Bedwars tarzı)", "Nodebuff", "Gapple",
]

KIT_STYLES = [
    "agresif rush", "savunmacı", "orta mesafe", "hit-and-run",
    "tank", "speed-based", "combo odaklı",
]

# ── Groq yardımcıları ─────────────────────────────────────────────────────────

def get_history(channel_id: int) -> list[dict]:
    return history.setdefault(channel_id, [])

def trim_history(channel_id: int):
    h = history[channel_id]
    if len(h) > MAX_HISTORY * 2:
        history[channel_id] = h[-(MAX_HISTORY * 2):]

async def ask_groq(channel_id: int, user_message: str, username: str) -> str:
    h = get_history(channel_id)
    h.append({"role": "user", "content": f"{username}: {user_message}"})
    trim_history(channel_id)
    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[SYSTEM_PROMPT] + h,
        max_tokens=512,
        temperature=0.7,
    )
    reply = response.choices[0].message.content.strip()
    h.append({"role": "assistant", "content": reply})
    return reply

async def generate_kit(mode: str, style: str) -> str:
    prompt = (
        f"Minecraft {mode} modu için '{style}' tarzında yaratıcı ve meta'ya uygun bir PvP kiti öner. "
        f"Kiti şu formatta ver:\n"
        f"**Kit Adı:** <isim>\n"
        f"**Mod:** {mode}\n"
        f"**Stil:** {style}\n"
        f"**Zırh:** <her parça için enchant ile birlikte listele>\n"
        f"**Silah:** <silah ve enchantlar>\n"
        f"**Envanter:** <önemli itemlar, iksirler, yiyecekler>\n"
        f"**Strateji:** <2-3 cümle kısa strateji ipucu>\n"
        f"Her seferinde farklı ve yaratıcı ol. Aynı kiti tekrar verme."
    )
    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[SYSTEM_PROMPT, {"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=1.0,
    )
    return response.choices[0].message.content.strip()

# ── Rapor Buton View ──────────────────────────────────────────────────────────

class RaporView(ui.View):
    def __init__(self, reported_user_id: int, reporter_id: int):
        super().__init__(timeout=None)
        self.reported_user_id = reported_user_id
        self.reporter_id = reporter_id

    def _yetkili_mi(self, interaction: discord.Interaction) -> bool:
        member = interaction.user
        return (
            member.guild_permissions.ban_members
            or member.guild_permissions.administrator
        )

    async def _raporu_guncelle(self, interaction, durum, renk, emoji, islem_yapan):
        embed = interaction.message.embeds[0]
        embed.color = renk
        embed.set_field_at(
            index=len(embed.fields) - 1,
            name="📋 Durum",
            value=f"{emoji} **{durum}** — {islem_yapan.mention} tarafından",
            inline=False,
        )
        embed.set_footer(text=f"İşlem: {islem_yapan.display_name} ({islem_yapan.id})")
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(embed=embed, view=self)

    @ui.button(label="🔨 Banla", style=discord.ButtonStyle.danger, custom_id="rapor_ban")
    async def ban_button(self, interaction: discord.Interaction, button: ui.Button):
        if not self._yetkili_mi(interaction):
            await interaction.response.send_message("❌ Ban yetkine olması lazım.", ephemeral=True)
            return
        try:
            user = await bot.fetch_user(self.reported_user_id)
            await interaction.guild.ban(user, reason=f"CentrAI rapor — {interaction.user}")
            await self._raporu_guncelle(interaction, "Banlandı", discord.Color.red(), "🔨", interaction.user)
            await interaction.response.send_message(f"✅ {user.mention} banlandı.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Botun yeterli yetkisi yok.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Hata: {e}", ephemeral=True)

    @ui.button(label="⚠️ Uyar", style=discord.ButtonStyle.primary, custom_id="rapor_uyar")
    async def uyar_button(self, interaction: discord.Interaction, button: ui.Button):
        if not self._yetkili_mi(interaction):
            await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
            return
        try:
            user = await bot.fetch_user(self.reported_user_id)
            try:
                await user.send(
                    f"⚠️ **{interaction.guild.name}** sunucusunda bir uyarı aldın.\n"
                    f"Moderatör: {interaction.user.display_name}"
                )
            except discord.Forbidden:
                pass
            await self._raporu_guncelle(interaction, "Uyarıldı", discord.Color.orange(), "⚠️", interaction.user)
            await interaction.response.send_message(f"✅ {user.mention} uyarıldı.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Hata: {e}", ephemeral=True)

    @ui.button(label="✅ Reddet", style=discord.ButtonStyle.success, custom_id="rapor_reddet")
    async def reddet_button(self, interaction: discord.Interaction, button: ui.Button):
        if not self._yetkili_mi(interaction):
            await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
            return
        await self._raporu_guncelle(interaction, "Reddedildi", discord.Color.green(), "✅", interaction.user)
        await interaction.response.send_message("✅ Rapor reddedildi.", ephemeral=True)

# ── is_reply_to_bot ───────────────────────────────────────────────────────────

def is_reply_to_bot(message: discord.Message) -> bool:
    ref = message.reference
    if ref is None:
        return False
    if ref.resolved and isinstance(ref.resolved, discord.Message):
        return ref.resolved.author.id == bot.user.id
    return False

async def send_reply(message: discord.Message, text: str):
    if len(text) > 1900:
        for chunk in [text[i:i+1900] for i in range(0, len(text), 1900)]:
            await message.reply(chunk)
    else:
        await message.reply(text)

# ── Events ────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    bot.add_view(RaporView(0, 0))
    print(f"✅  CentrAI is online as {bot.user} (id: {bot.user.id})")
    print(f"    Model   : {MODEL}")
    print(f"    Trigger : '{TRIGGER}' veya bota reply")
    print("─" * 45)

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    content = message.content.strip()

    if content.startswith(TRIGGER):
        query = content[len(TRIGGER):].strip()
        if not query:
            await message.reply("Selam! Centra tier list hakkında ne sormak istersin? 🎮")
            return
        async with message.channel.typing():
            try:
                reply = await ask_groq(message.channel.id, query, message.author.display_name)
            except Exception as e:
                reply = f"⚠️ Groq hatası: {e}"
        await send_reply(message, reply)
        return

    if is_reply_to_bot(message):
        async with message.channel.typing():
            try:
                reply = await ask_groq(message.channel.id, content, message.author.display_name)
            except Exception as e:
                reply = f"⚠️ Groq hatası: {e}"
        await send_reply(message, reply)
        return

    await bot.process_commands(message)

# ── Commands ──────────────────────────────────────────────────────────────────

@bot.command(name="clear")
async def clear_history(ctx: commands.Context):
    history.pop(ctx.channel.id, None)
    await ctx.send("🗑️ Konuşma geçmişi temizlendi!")


@bot.command(name="kityap")
async def kit_suggest(ctx: commands.Context, *, mod: str = None):
    selected_mode = mod.strip() if mod else random.choice(KIT_MODES)
    selected_style = random.choice(KIT_STYLES)
    async with ctx.typing():
        try:
            kit_text = await generate_kit(selected_mode, selected_style)
        except Exception as e:
            await ctx.send(f"⚠️ Kit üretilemedi: {e}")
            return
    embed = discord.Embed(title="⚔️ Rastgele Kit Önerisi", description=kit_text, color=0x00FF88)
    embed.set_footer(text=f"🎲 Mod: {selected_mode} | Stil: {selected_style} | Powered by CentrAI")
    await ctx.send(embed=embed)


@bot.command(name="raporsetup")
@commands.has_permissions(administrator=True)
async def rapor_setup(ctx: commands.Context):
    text_channels = [ch for ch in ctx.guild.text_channels]
    if not text_channels:
        await ctx.send("❌ Sunucuda metin kanalı bulunamadı.")
        return

    class KanalSecView(ui.View):
        def __init__(self):
            super().__init__(timeout=60)

        @ui.select(
            placeholder="Rapor kanalını seç...",
            options=[
                discord.SelectOption(label=f"#{ch.name}", value=str(ch.id))
                for ch in text_channels[:25]
            ],
        )
        async def kanal_sec(self, interaction: discord.Interaction, select: ui.Select):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❌ Sadece komutu kullanan kişi seçim yapabilir.", ephemeral=True)
                return
            channel_id = int(select.values[0])
            set_report_channel(ctx.guild.id, channel_id)
            channel = ctx.guild.get_channel(channel_id)
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)
            await interaction.response.send_message(
                f"✅ Rapor kanalı **#{channel.name}** olarak ayarlandı!",
            )
            self.stop()

    embed = discord.Embed(
        title="⚙️ Rapor Kanalı Kurulumu",
        description="Aşağıdan raporların gönderileceği kanalı seç:",
        color=0x5865F2,
    )
    await ctx.send(embed=embed, view=KanalSecView())


@bot.command(name="rapor")
async def rapor(ctx: commands.Context, kullanici: discord.Member = None, *, sebep: str = None):
    if kullanici is None:
        await ctx.send("❌ Kullanım: `!centra_rapor @kullanıcı <sebep>`")
        return
    if sebep is None:
        sebep = "Sebep belirtilmedi."

    channel_id = get_report_channel(ctx.guild.id)
    if channel_id is None:
        await ctx.send("❌ Rapor kanalı ayarlanmamış. Yönetici `!centra_raporsetup` komutuyla ayarlasın.")
        return

    rapor_kanali = ctx.guild.get_channel(channel_id)
    if rapor_kanali is None:
        await ctx.send("❌ Ayarlı rapor kanalı bulunamadı, yönetici tekrar kurulum yapmalı.")
        return

    embed = discord.Embed(title="🚨 Yeni Oyuncu Raporu", color=0xFF4444, timestamp=ctx.message.created_at)
    embed.add_field(name="👤 Raporlanan", value=f"{kullanici.mention}\n`{kullanici}` (ID: {kullanici.id})", inline=True)
    embed.add_field(name="📢 Raporlayan", value=f"{ctx.author.mention}\n`{ctx.author}`", inline=True)
    embed.add_field(name="📝 Sebep", value=sebep, inline=False)
    embed.add_field(name="📋 Durum", value="⏳ Bekliyor — moderatör incelemesi bekleniyor", inline=False)
    embed.set_thumbnail(url=kullanici.display_avatar.url)
    embed.set_footer(text=f"Rapor #{ctx.message.id}")

    view = RaporView(reported_user_id=kullanici.id, reporter_id=ctx.author.id)
    await rapor_kanali.send(embed=embed, view=view)
    await ctx.send(f"✅ {kullanici.mention} için raporun alındı ve moderatörlere iletildi.", delete_after=10)
    try:
        await ctx.message.delete(delay=10)
    except discord.Forbidden:
        pass


@bot.command(name="help")
async def show_help(ctx: commands.Context):
    embed = discord.Embed(
        title="⚔️ CentrAI — Kullanım Kılavuzu",
        description="Centra Minecraft Tier Testing sunucusu için AI asistanı",
        color=0x00FF88,
    )
    embed.add_field(
        name="📌 AI Komutları",
        value=(
            f"`{TRIGGER} <soru>` — AI'a soru sor\n"
            "Bota **reply** at — konuşmaya devam et\n"
            "`!centra_clear` — Geçmişi temizle"
        ),
        inline=False,
    )
    embed.add_field(
        name="⚔️ Kit Komutları",
        value=(
            "`!centra_kityap` — Rastgele mod için kit üret\n"
            "`!centra_kityap HCF` — Belirli mod için kit üret"
        ),
        inline=False,
    )
    embed.add_field(
        name="🚨 Rapor Komutları",
        value=(
            "`!centra_rapor @kullanıcı <sebep>` — Oyuncu raporla\n"
            "`!centra_raporsetup` — Rapor kanalı ayarla (sadece admin)"
        ),
        inline=False,
    )
    embed.set_footer(text=f"Model: {MODEL}")
    await ctx.send(embed=embed)

# ── Error handling ────────────────────────────────────────────────────────────

@rapor_setup.error
async def rapor_setup_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu sadece adminler kullanabilir.")

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
