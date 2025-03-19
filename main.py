import sys
from dotenv import load_dotenv
import os
import asyncio
from src.bot import create_bot


async def main():
    # check if .env file exists
    try:
        with open('.env') as f:
            pass
    #If not create it and ask the user to enter the data
    except FileNotFoundError:
        # We create the .env file
        try:
            with open('.env', 'w') as f:
                #ask the user for the  discord token
                discord_token = input("Enter your discord token: ")
                f.write(f"DISCORD_TOKEN={discord_token}\n")
                #ask the user for the prefix
                prefix = input("Enter your prefix: ")
                f.write(f"PREFIX={prefix}\n")
                #ask the user for the owner id
                owner_id = input("Enter your owner id: ")
                f.write(f"OWNER_ID={owner_id}\n")
                #save the file
                f.close()

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    #We extract environment variables
    try:
        load_dotenv(dotenv_path='.env')

        DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        PREFIX = os.getenv('PREFIX')
        OWNER_ID = os.getenv('OWNER_ID')

        if not DISCORD_TOKEN or not PREFIX or not OWNER_ID:
            raise Exception("Missing environment variables")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Create and run the bot
    bot = create_bot(PREFIX, OWNER_ID)
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())