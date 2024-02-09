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
        model, temperature, system_message, user_instructions = customize_chatbot()

    conversation = initialize_conversation(user_name, system_message, user_instructions)
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
    customize = console.input("[italic]Do you want to customize the model, temperature, or system instructions? (y/n) [/italic]").strip().lower()

    rich_print("\n[italic]Type [encircle red]'quit'[/encircle red] to exit the program at any time.[italic/]")

    return user_name, customize


def customize_chatbot():
    """
    If the user chooses to customize the chatbot, this function will run.
    """
    while True:
        rich_print("\n[bold]Customize Einstein[/]")
        rich_print("\n[italic]If you want to use the default settings, just press [green bold]'Enter'[/green bold][/italic]/n")
        rich_print("\n[italic]Default settings: Model: gpt-4, Temperature: 0.8, System Message: Default[/italic]/n")
        rich_print("\n[italic]If you want more info about any option below, type [green bold]'help'[/green bold][/italic]/n/n")

        model = get_input_with_help("Which [bold]model[/] would you like to use? [italic](gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview)[/] ")
        temperature = get_input_with_help("What [bold]temperature[/] would you like to use? [italic](0.0 - 2.0)[/] ")
        user_instructions = get_input_with_help("What [bold]instructions[/] would you like to provide to the AI? [italic][/] ")
        system_message = get_input_with_help("What [bold]system message[/] would you like to use? [italic](default, academic_advisor, math_tutor)[/] ")

        if confirm_customization(model, temperature, user_instructions, system_message):
            return model, round(float(temperature), 1), system_message, user_instructions


def get_input_with_help(prompt):
    """
    Get user input with help option.
    """
    while True:
        user_input = console.input(prompt)
        if user_input.lower() == "help":
            show_help()
        else:
            return user_input


def show_help():
    """
    If the user types "help" at any time, this function will run.
    """
    help_table = Table(box=box.SQUARE_DOUBLE_HEAD)
    help_table.add_column("Help Options", header_style="bold cyan", justify="center")
    help_table.add_row("[bold]Model[/]: The model used to generate responses. The default is gpt-4.")
    help_table.add_row("[bold]Temperature[/]: The randomness of the AI's responses. Higher temperatures will result in more random responses. The default is 0.8.")
    help_table.add_row("[bold]Instructions[/]: Any additional context or instructions for the AI to follow.")
    help_table.add_row("[bold]System Message[/]: The system message to provide to the AI. The default is 'default', a general assistant.")
    rich_print(help_table)


def confirm_customization(model, temperature, user_instructions, system_message):
    """
    Confirm customization options with the user.
    """
    rich_print("\n[bold]Customization Summary[/]")
    rich_print(f"\n[bold]Model[/]: {model}")
    rich_print(f"\n[bold]Temperature[/]: {temperature}")
    rich_print(f"\n[bold]Instructions[/]: {user_instructions}")
    rich_print(f"\n[bold]System Message[/]: {system_message}")
    confirmation = console.input("\n[bold light_cyan1]Are these customization options correct? ([green]y[/green]/[red]n[/red])[/] ").strip().lower()
    return confirmation == 'y' or confirmation == 'yes'




def initialize_conversation(user_name, system_message, user_instructions):
    """
    Initializes the conversation.

    Args:
        user_name (str): The name of the user
        system_prompt (str): The custom prompt entered by user (OPTIONAL)

    Returns:
        list: A list containing a system message with instructions for Einstein.
    """
    return [  
        {   
            'role':'system', 'content':f'''Your primary instructions are below, delimited by three asterisks./n
            
            ***{system_message}***/n
            
            The name of the person you are talking to is {user_name}./n
            If there is any additional context or instructions for you to follow, they will be entered below,
            delimited by three backticks./n
            
            ```{user_instructions}```
            '''
        },
    ]


def get_completion_from_messages(messages, model, temperature):
    '''Set model and temperature for conversation, send message to OpenAI and get response'''
    response = client.chat.completions.create(model=model,
    messages = messages,
    temperature = temperature)
    return response.choices[0].message.content


def create_conversation_file(user_name):
    """
    Create a file to store the conversation.

    Args: 
        user_name (str): The name of the user.

    Returns:
        str: The filename of the conversation file.
    """

    if not os.path.exists("conversations"):
        os.makedirs("conversations")

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    existing_files = [f for f in os.listdir("conversations")]

    # Check if user wants to customize file name 
    customize_name = console.input("\n[bold light_cyan1]Do you want to customize the conversation file name? ([green]y[/green]/[red]n[/red])[/] ").strip().lower()

    # Custom file naming logic
    if customize_name == 'y' or customize_name == 'yes':
        while True:
            filename = console.input("\n[bold light_cyan1]Enter a custom file name: [/]")
            if filename in existing_files:
                rich_print("\n[bold red]That file already exists. Please enter a different name.[/]")
            else:
                break

    # Default file naming logic
    else:
        # Find the highest conversation count and increment by 1
        highest_count = max([int(f.split("_")[-1].split(".")[0]) for f in existing_files if f.startswith(f"{user_name}_")], default=0)
        conversation_count = highest_count + 1

        # Construct the filename
        filename = f"{user_name}_{timestamp}_{conversation_count:03d}.txt"

    return filename


def have_conversation(conversation, user_name, model, temperature):
    """
    Facilitates the conversation between the user and the character.

    Args:
        conversation (list): A list of conversation messages.
        user_name (str): The user's name.

    Returns:
        None
    """
    filename = create_conversation_file(user_name)
    conversation_file = open(os.path.join("conversations", filename), "w", encoding="utf-8")

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

