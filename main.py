import os
import random
import wikipedia
from dotenv import load_dotenv
from openai import OpenAI
import itertools
import threading
import time
import sys


# ANSI Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
HEADER = '\033[95m'
UNDERLINE = '\033[4m'


TOPICS_BY_CATEGORY = {
    "lifestyle": [
        "Cooking", "Fashion", "Film", "Music", "Yoga", "Gardening"
    ],
    "science": [
        "Photosynthesis", "Black hole", "DNA", "Gravitational wave",
        "Theory of relativity", "Volcano", "Quantum computing"
    ],
    "politics": [
        "Democracy", "Socialism", "Capitalism", "Communism",
        "Monarchy", "Republic"
    ]
}


def print_logo():
    print(rf"""{YELLOW}
  ███████╗ █████╗ ██╗  ██╗███████╗    ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗ 
  ██╔════╝██╔══██╗██║ ██╔╝██╔════╝    ██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗
  █████╗  ███████║█████╔╝ █████╗      █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝
  ██╔══╝  ██╔══██║██╔═██╗ ██╔══╝      ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
  ██║     ██║  ██║██║  ██╗███████╗    ██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║
  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝

         Separate true facts from fake stories — powered by Wikipedia & AI!{RESET}
         """)


def print_welcome_message():
    print("Welcome to FAKE FINDER")
    print("___________________________________________________________________________________")


def get_user_input():
    user_input_name = input(f"{BOLD}Please provide your name: {RESET}")

    while True:
        user_input_level = input(f"{BOLD}Please provide the level of the game (easy/medium/hard): {RESET}".strip())
        if user_input_level in ["easy", "medium", "hard"]:
            break
        print(f"{RED}Please enter easy, medium or hard.{RESET}\n")

    while True:

        try:
            user_input_rounds = int(input(f"{BOLD}How many rounds do you want to play? (1-10) {RESET}").strip())
            if 1 <= user_input_rounds <= 10:
                break
            print(f"{RED}Please enter a valid number.{RESET}\n")

        except ValueError:
            print(f"{RED}Please enter a number.{RESET}\n")

    return user_input_name, user_input_level, user_input_rounds


def get_user_category():
    print(f"{YELLOW}==================================================================================={RESET}")
    print("Please choose the category of the game you wish to play:")
    print("1. Lifestyle")
    print("2. Science")
    print("3. Politics")

    while True:
        user_input_category = input(f"{YELLOW}\nPlease provide your choice (1/2/3): {RESET}".strip())

        if user_input_category == "1":
            topic = "Lifestyle"
            break
        elif user_input_category == "2":
            topic = "Science"
            break
        elif user_input_category == "3":
            topic = "Politics"
            break

        print(f"{RED}Please enter a valid number.{RESET}\n")

    topic_list = TOPICS_BY_CATEGORY[topic.lower()]

    return topic_list


def get_user_topics(topics):
    print("___________________________________________________________________________________")

    list_index = []
    for index, topic in enumerate(topics):
        print(f"{index + 1}. {topic}")
        list_index.append(index + 1)

    while True:

        try:
            user_input_topic = input(f"{YELLOW}\nPlease provide your choice (select one number): {RESET}".strip())

            if int(user_input_topic) in list_index:
                return topics[int(user_input_topic) - 1]

            print(f"{RED}Please enter a valid number.{RESET}\n")

        except ValueError:
            print(f"{RED}Please enter a number.{RESET}\n")


def get_article_from_wikipedia(title):
    page = wikipedia.WikipediaPage(title=title, pageid=None, redirect=True, preload=False, original_title=u'')
    # page = wikipedia.summary(title, sentences=0, chars=0, auto_suggest=True, redirect=True)
    return page.content


# Create a threading event
stop_event = threading.Event()


def animate():
    detective_emoji = [
        "🔍(•‿•)", " 🔍( •‿•)", " 🔍( •‿•)", "  🔍(  •‿•",
        "  🔍(  -‿-", "  🔍(  •‿•", " 🔍( •‿•)", " 🔍( •‿•)",
        "🔍(•‿•)", "🔍(-‿-)", "🔍(•‿•)", " 🔍(•‿• )",
        " 🔍(•‿• )", "  🔍•‿•  )", "  🔍-‿-  )",
        "  🔍•‿•  )", " 🔍(•‿• )", " 🔍(•‿• )"
    ]
    for c in itertools.cycle(detective_emoji):
        if stop_event.is_set():  # check if stop signal sent
            break
        sys.stdout.write('\rSearching for facts ... ' + c)
        sys.stdout.flush()
        time.sleep(0.3)
    sys.stdout.write('\r')


def generate_facts(article_content, level):
    # Start animation thread
    stop_event.clear()
    animation_thread = threading.Thread(target=animate)
    animation_thread.start()

    # Load .env file
    load_dotenv()

    # Access API key
    api_keys = os.environ.get('OPENAI_API_KEY')

    # OpenAI Function
    client = OpenAI()

    response = client.responses.create(
        model="gpt-5-nano",
        input=f"""
        # Inputs: 
        The content of the article is: {article_content}

        The selected level is: {level}

        # Role 
        You are part of a game called Fake Finder. A fact checking game that provide real facts and one fake fact.

        # Goal
        Select 3 factual sentences that are present in the article, these will be the true sentences. 
        Generate 1 wrong fake sentence based on a fourth one from the article, this one will be the false sentence.

        # Rules
        - The first sentence should always be wrong
        - The Fake sentence should have boolean "False"
        - The Factual sentence should have boolean "True"
        - The sentences should not have more than 20 words
        - Don't hallucinate or generate random factual sentences
        - Focus only on the given input
        - We have 3 different levels, these levels will define the complexity of the sentences, are the definitions of them: 
          - easy = A child is familiar with all sentences and can identify the fake sentence
          - medium = An adult is familiar with all sentences and can identify the fake sentence
          - hard = An adult can identify the fake sentence with challenge
        - Select the fact sentences and generate the fake sentence based on the selected level: {level}

        # Output: (fake_sentence @ False) | (fact_sentence_1 @ True) | (fact_sentence_2 @ True) | (fact_sentence_3 @ True)
        """
    )

    # Stop animation
    stop_event.set()
    animation_thread.join()

    return response.output_text


def convert_string_to_list(string):
    result = []
    items = string.strip().split("|")  # remove brackets and split
    for item in items:
        parts = item.split("@")
        sentence = parts[0].strip()[1:]
        boolean = parts[1].strip()[:-1]
        if boolean == "True":
            boolean = True
        if boolean == "False":
            boolean = False
        result.append((sentence, boolean))
    return result


def display_randomized_facts(facts):
    print("___________________________________________________________________________________")
    # Randomize the fact list
    random.shuffle(facts)

    # Display facts in the console
    for index, (fact, boolean) in enumerate(facts):
        print(f"{index + 1}. {fact}")

    return facts


def check_answer(facts):
    while True:
        try:
            user_answer = input(f"{YELLOW}\nPlease enter the number of the fake sentence (1/2/3/4): {RESET}".strip())

            if 1 <= int(user_answer) <= 4:
                break
            print(f"{RED}Please enter a valid number.{RESET}")

        except ValueError:
            print(f"{RED}Please enter a valid number.{RESET}")


    correct_sentence = ""
    boolean_index = 0
    for fact_tuple in facts:
        if fact_tuple[1] == False:
            boolean_index = facts.index(fact_tuple)
            correct_sentence = fact_tuple[0]

    if int(user_answer) - 1 == boolean_index:
        print(f"{GREEN}You have the correct answer!{RESET}")
        return True
    else:
        print(f"{RED}You have the wrong end of the stick, try again!{RESET}")
        print("\nThe fake sentence is:")
        print(f'"{correct_sentence}"')
    return None


def print_display_score(name, score, round_number):
    print(f"\nYOUR SCORE: {score}/{round_number}{RESET}")


def main():
    print_logo()
    # 1. Welcome message
    print_welcome_message()


    while True:
        user_input_name, user_input_level, user_input_rounds = get_user_input()
        score = 0
        for round in range(1, user_input_rounds + 1):
            print(f"\n{YELLOW}================================== Round {round} ========================================{RESET}")
            print(f"PLAYER: {user_input_name}    |    YOUR SCORE: {score}    |    YOUR LEVEL: {user_input_level}")

            # 2. Show the game menu.
            topic_list = get_user_category()
            title = get_user_topics(topic_list)

            # 3. Get article from Wikipedia (e.g. Wikipedia Article: American presidents)
            article_content = get_article_from_wikipedia(title)

            # 4. Give the information to OpenAI from Wikipedia
            facts = generate_facts(article_content, user_input_level)
            transformed_fact = convert_string_to_list(facts)

            # 5. Display the four sentences on the screen
            randomized_facts = display_randomized_facts(transformed_fact)

            is_correct = check_answer(randomized_facts)
            if is_correct == True:
                score += 1
            print_display_score(user_input_name, score, round)

        quit_message = input(f"{YELLOW}\nWould you like to play again? (Y/N): {RESET}")
        if quit_message == "N" or quit_message == "n":
            print("Thank you for playing!")
            break


if __name__ == "__main__":
    main()
