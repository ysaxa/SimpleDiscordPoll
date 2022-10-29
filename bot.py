import os
import json
import discord # type: ignore
from threading import RLock
from dotenv import load_dotenv

load_dotenv()

temp = os.getenv("TOKEN")
assert temp is not None
TOKEN: str = temp

temp = os.getenv("CHANNEL")
assert temp is not None
CHANNELID: int = int(temp)

temp = os.getenv("POLL_TIMEOUT")
assert temp is not None
pollTimeout: int = int(temp)

temp = os.getenv("POLL_VALUES")
assert temp is not None
candidates: str = temp.split(',')

# View with buttons
class Poll(discord.ui.View):
	def __init__(self, client: discord.Client):
		super().__init__(timeout=pollTimeout)
		self.msg: discord.Message

		self.votes: dict = {}
		self.voteLock: RLock = RLock()

		def getCallback(vote: str):
			async def callback(interaction: discord.Interaction):
				with self.voteLock:
					self.votes[interaction.user.id] = vote
				await interaction.response.send_message(f"Vote pour {vote} pris en compte.", ephemeral=True)

			return callback

		for candidate in candidates:
			button: discord.ui.Button = discord.ui.Button(label=candidate, style=discord.ButtonStyle.blurple)
			button.callback = getCallback(candidate)
			self.add_item(button)

	async def on_timeout(self):
		for item in self.children:
			if isinstance(item, discord.ui.Button):
				item.style = discord.ButtonStyle.grey
				item.disabled = True
		await self.msg.edit(view=self)

		with self.voteLock:
			await self.msg.reply('\n'.join([
				f'{candidate}: {sum([1 if v == candidate else 0 for v in self.votes.values()])}'
				for candidate in candidates
			]))

		await client.close()

class MyClient(discord.Client):
	async def on_ready(self):
		print(f'Logged on as {self.user} ({self.user.id})')
		channel: discord.TextChannel = discord.utils.get(self.get_all_channels(), id=CHANNELID)
		print(f'Will send poll in channel {channel.name}')

		poll = Poll(client)
		msg: discord.Message = await channel.send("Vote", view=poll)
		poll.msg = msg

intents = discord.Intents.default()

client = MyClient(intents=intents)
client.run(TOKEN)
