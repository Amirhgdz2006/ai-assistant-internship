def run_chatbot():
    process = True

    user_name = input("Bot: Hi, I am a simple chatbot that answers a few basic questions.\nBot: What is your name?\nYou: ").lower()
    print(f'Bot: Hi {user_name} How can I help you today?')


    responses = {
        "hi": f"Hi {user_name}",
        "how are you": "I am just a bot, but I am doing fine. Thanks for asking",
        "what is your name": "My name is JARVIS.",
        "what can you do": "I can answer a few basic questions",
        "what time is it": "Sorry, I am not able to tell the time or date",
        "thank you": "You're welcome"
    }

    while process:
        entry = input('You: ').lower()

        if 'exit' in entry or 'end' in entry or 'bye' in entry:
            process = False
            print('Bot: Goodbye and Have a great day')
        else:

            matched = False
            for key in responses:
                if key in entry:
                    response = responses[key]

                    print(f"Bot: {response}")
                    matched = True

            if matched == False:
                print("Bot: Sorry, I didn't understand what you said. Can you rephrase it?")


run_chatbot()

