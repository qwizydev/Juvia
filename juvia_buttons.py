# buttons.py

import discord
from discord.ui import Button, View


class ConfirmationView(View):
    def __init__(self, timeout=15):
        super().__init__(timeout=timeout)
        self.result = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, button: Button, interaction: discord.Interaction):
        self.result = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_button(self, button: Button, interaction: discord.Interaction):
        self.result = False
        self.stop()
