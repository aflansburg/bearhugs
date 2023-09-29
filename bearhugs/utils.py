import os
import getpass


def get_open_ai_key():
    open_ai_api_key = os.getenv('OPENAI_API_KEY')

    if not open_ai_api_key:
        print("No OpenAI key found in environment variables.")
        open_ai_api_key = getpass.getpass('Enter your OpenAI API key: ')

        if not open_ai_api_key:
            print("No OpenAI key provided. Exiting.")
            exit()

    return open_ai_api_key
