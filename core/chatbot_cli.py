from core.responses import get_responses


def run_chatbot():
    try:
        process = True

        responses = get_responses()

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
    except KeyboardInterrupt:
        print('The program ended.')
