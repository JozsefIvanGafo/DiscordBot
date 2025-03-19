import sys
from dotenv import load_dotenv
import os


if __name__ == "__main__":
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
        load_dotenv()

        DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        PREFIX = os.getenv('PREFIX')
        OWNER_ID = os.getenv('OWNER_ID')
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    
