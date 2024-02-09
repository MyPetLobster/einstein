import datetime
import os

from openai import OpenAI
from dotenv import load_dotenv
from rich import print as rich_print
from rich.console import Console
from rich import box
from rich.table import Table

# "system_messages" is a list of dicts with the following keys: "default", "academic_advisor", "math_tutor"
from instructions import system_messages

load_dotenv()
client = OpenAI()
console = Console()

# Default Settings
MODEL = "gpt-4"
TEMPERATURE = 0.8
SYSTEM_MESSAGE = system_messages["default"]


def main():
    model = MODEL
    temperature = TEMPERATURE
    system_message = SYSTEM_MESSAGE
    user_instructions = ""

    user_name, customize = greet_user()

    if customize == 'y' or customize == 'yes':
        model, temperature, user_instructions, system_message = customize_chatbot()

    

    conversation = initialize_conversation(user_name, user_instructions, system_message)
    have_conversation(conversation, user_name, model, temperature)


def greet_user():
    intro_table = Table(box=box.SQUARE_DOUBLE_HEAD)
    intro_table.add_column("This is Einstein, your personal assistant.", header_style="bold cyan", justify="center")
    intro_table.add_row('''[bold chartreuse3]Einstein is a conversational AI that can help you with a variety of tasks.''')
    intro_table.add_row(' ')
    intro_table.add_row('[bold deep_pink4]Einstein - By Cory Suzuki[/]')
    intro_table.add_row(' ')
    intro_table.add_row('[bold chartreuse3] https://github.com/MyPetLobster/einstein[/]')
    rich_print("\n")
    rich_print(intro_table)

    user_name = console.input("What should I call you? ")
    customize = console.input("[italic]Do you want to customize the model, temperature, or system instructions? (y/n) [/italic]").lower().strip()

    rich_print("\n[italic]Type [encircle red]'quit'[/encircle red] to exit the program at any time.[italic/]")

    return user_name, customize


def customize_chatbot():
    """
    If the user chooses to customize the chatbot, this function will run.

    No Args

    Returns: Tuple containing {model, temperature, instructions, system_message}
    """
    rich_print("\n[bold]Customize Einstein[/]")
    rich_print("\n[italic]If you want to use the default settings, just press [green bold]'Enter'[/green bold][/italic]/n")
    rich_print("\n[italic]Default settings: Model: gpt-4, Temperature: 0.8, System Message: Default[/italic]/n")
    rich_print("\n[italic]If you want more info about any option below, type [green bold]'help'[/green bold][/italic]/n/n")

    model = console.input("Which [bold]model[/] would you like to use? [italic](gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview)[/]/n")
    temperature = round(float(console.input("What [bold]temperature[/] would you like to use? [italic](0.0 - 2.0)[/] "), 1))
    user_instructions = console.input("What [bold]instructions[/] would you like to provide to the AI? [italic][/] ")
    system_message = console.input("What [bold]system message[/] would you like to use? [italic](default, academic_advisor, math_tutor)[/] ")
    
    return model, temperature, user_instructions, system_message

    
# Function to initialize conversation and provide system message to the AI
def initialize_conversation(user_name, user_instructions, system_message):
    """
    Initializes the conversation.

    Args:
        user_name (str): The name of the user
        system_prompt (str): The custom prompt entered by user (OPTIONAL)

    Returns:
        list: A list containing a system message with instructions for the character.
    """
    return [  
        {   
            'role':'system', 'content':f'''{system_message}/n
            
            The name of the person you are talking to is {user_name}./n
            If there is any additional context or instructions for you to follow, they will follow this sentence./n
            
            {user_instructions}
            '''
        },
    ]


# Function to set completion parameters and get response for conversation
def get_completion_from_messages(messages, model, temperature):
    '''Set model and temperature for conversation, send message to OpenAI and get response'''
    response = client.chat.completions.create(model=model,
    messages=messages,
    temperature=temperature)
    return response.choices[0].message.content


# Function to continue conversation
def have_conversation(conversation, user_name, model, temperature):
    """
    Facilitates the conversation between the user and the character.

    Args:
        conversation (list): A list of conversation messages.
        user_name (str): The user's name.

    Returns:
        None
    """
    # Create the "conversations" folder if it doesn't exist
    if not os.path.exists("conversations"):
        os.makedirs("conversations")

    # Generate a timestamp to use in the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")

    # Check for existing conversation files
    existing_files = [f for f in os.listdir("conversations") if f.startswith(f"{user_name}_")]

    if existing_files:
        # Find the highest conversation count and increment by 1
        highest_count = max([int(f.split("_")[-1].split(".")[0]) for f in existing_files])
        conversation_count = highest_count + 1
    else:
        conversation_count = 1

    # Construct the filename
    filename = f"{user_name}_{timestamp}_{conversation_count:03d}.txt"
    conversation_file = open(os.path.join("conversations", filename), "w", encoding="utf-8")

    # Have the conversation
    try:
        while True:
            user_input = console.input("\n[bold light_cyan1]You: [/]")
            conversation_file.write(f"You: {user_input}\n\n")
            if user_input.lower() == 'quit':
                rich_print("\n[bold]Do you want to save this conversation? ([green]y[/green]/[red]n[/red])[/]")
                save = console.input("\n[bold light_cyan1]You: ")
                if save.lower() == 'n':
                    conversation_file.close()
                    os.remove(os.path.join("conversations", filename))
                    rich_print("\n[bold cyan]Goodbye![/]\n")
                    exit()
                else:
                    rich_print(f"\n[bold cyan]Conversation saved to conversations/{filename}[/]\n")
                    conversation_file.close()
                    exit()
            conversation.append({'role': 'user', 'content': user_input})
            response = get_completion_from_messages(conversation, model, temperature)
            conversation.append({'role': 'assistant', 'content': response})

            rich_print(f"\n[bold light_yellow3]Einstein: [/]", response)
            conversation_file.write(f"Einstein: {response}\n\n")

    finally:
        conversation_file.close()


if __name__ == "__main__":
    main()

