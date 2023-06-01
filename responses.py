def handle_response(message) -> str:
    p_message = message.lower()

    if p_message == 'help':
        return "Use the command /help for help instead!"