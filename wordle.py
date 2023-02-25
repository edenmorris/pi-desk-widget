import string
import secrets
import json
from json import JSONDecodeError
import sys
import PySimpleGUI as sg

UNUSED_VOWEL = 5
UNUSED_CONSONANT = 6
USED_VOWEL = 2
USED_CONSONANT = 1

class GuessStatus():
    """ TODO docstring """
    def __init__(self):
        self.weights = 0
        self.valid_words = []
        self.grey_status = {}
        self.yellow_status = {}
        self.green_status = {}
        self.best_guess = None
        self.turn_counter = 0
        self.guess_status = ['','','','','']

    def fill_info(self, guess=None, status=None):
        for i, char in enumerate(status):
            if char == 'c':
                self.grey_status[guess[i]] = [i]

            if char == 'b':
                if self.yellow_status.get(guess[i]):
                    self.yellow_status[guess[i]].append(i)
                else:
                    self.yellow_status[guess[i]] = [i]

            if char == 'a':
                if self.green_status.get(guess[i]):
                    self.green_status[guess[i]].append(i)
                else:
                    self.green_status[guess[i]] = [i]

    def recommended_answer(self):
        vowels = ['a', 'e', 'i', 'o', 'u']
        max_sum = 0
        temp_sum = 0

        for word in self.valid_words:
            for char in word:
                if char in self.yellow_status.keys() or char in self.green_status.keys() or char in self.grey_status.keys():
                    if char in vowels:
                        temp_sum += self.weights.get(char) * UNUSED_VOWEL
                    else:
                        temp_sum += self.weights.get(char) * UNUSED_CONSONANT
                else:
                    if char in vowels:
                        temp_sum += self.weights.get(char) * USED_VOWEL
                    else:
                        temp_sum += self.weights.get(char) * USED_CONSONANT

                if word.count(char) > 1:
                    temp_sum = temp_sum / 2

            if temp_sum > max_sum:
                self.best_guess = word
                max_sum = temp_sum
            temp_sum = 0

    def check_guess(self, sim_guess, sim_answer) -> str:
        self.guess_status = ['','','','','']
        self.check_green(sim_guess, sim_answer)
        self.check_yellow(sim_guess, sim_answer)
        self.check_grey()

        return ''.join(self.guess_status)

    def check_green(self, sim_guess, sim_answer):
        for i, char in enumerate(sim_guess):
            if char == sim_answer[i]:
                self.guess_status[i] = 'a'

    def check_yellow(self, sim_guess, sim_answer):
        repeating_chars_in_word = dict.fromkeys(string.ascii_lowercase, 0)

        for i, char in enumerate(sim_answer):
            repeating_chars_in_word[char] = sim_answer.count(char)

            if self.guess_status[i] == 'a':
                repeating_chars_in_word[char] = repeating_chars_in_word.get(char) - 1

        for i, char in enumerate(sim_guess):

            if char in sim_answer and not (char == sim_answer[i]) and repeating_chars_in_word.get(char):
                self.guess_status[i] = 'b'
                repeating_chars_in_word[char] = repeating_chars_in_word.get(char) - 1

    def check_grey(self):
        self.guess_status = ["c" if x == '' else x for x in self.guess_status]

    def filter_functions(self):
        self.filter_yellow()
        self.filter_green()
        self.filter_grey()

    def filter_grey(self):
        def valid_grey(word: str) -> bool:
            valid = True

            for char, _ in self.grey_status.items():
                if char in word and not self.yellow_status.get(char) and not self.green_status.get(char):
                    valid = False

            return valid

        self.valid_words = [word for word in self.valid_words if valid_grey(word)]

    def filter_green(self):
        def valid_green(word: str) -> bool:
            valid = True

            for char, status in self.green_status.items():
                for location in status:
                    if char != word[location]:
                        valid = False

            return valid

        self.valid_words = [word for word in self.valid_words if valid_green(word)]

    def filter_yellow(self):
        def valid_yellow(word: str) -> bool:
            valid = True

            for char, status in self.yellow_status.items():
                for location in status:
                    if char not in word or char == word[location]:
                        valid = False

            return valid


        self.valid_words = [word for word in self.valid_words if valid_yellow(word)]


def read_file(filepath: str) -> list:

    with open(filepath, 'r', encoding='utf-8') as f:
        contents = f.readlines()

    stripped_contents = [line.rstrip() for line in contents]

    return stripped_contents


def calculate_character_weights(raw_inputs: list) -> dict:

    character_weights = dict.fromkeys(string.ascii_lowercase, 0)

    for word in raw_inputs:
        for char in word:
            character_weights[char] += 1

    return character_weights


def get_weights() -> list:
    try:
        with open('/home/eden/workspace/weights.json', 'r', encoding='utf-8') as fh:
            character_weights = json.load(fh)
    except FileNotFoundError:
        raw_inputs = read_file('/home/eden/workspace/words_alpha.txt')
        character_weights = calculate_character_weights(raw_inputs)

        with open("/home/eden/workspace/weights.json", "w",encoding='utf-8') as fp:

            total_sum = 0
            for value in character_weights.values():
                total_sum += value   
            for key, value in character_weights.items():
                character_weights[key] = int(value * 10_000 / total_sum)

            json.dump(character_weights, fp)

    return character_weights


def check_winner(turn_counter: int, status=None):
    if status == 'aaaaa':
        try:
            with open('/home/eden/workspace/score_sheet.json', 'r', encoding='utf-8') as fh:
                score_sheet = json.load(fh)

            with open('/home/eden/workspace/score_sheet.json', 'w', encoding='utf-8') as fh:

                score_sheet['games'] = score_sheet.get('games') + 1
                if turn_counter < 6:
                    score_sheet['wins'] = score_sheet.get('wins') + 1
                score_sheet['average'] = score_sheet.get('wins') / score_sheet.get('games')
                score_sheet['turns'] = score_sheet.get('turns') + turn_counter + 1

                json.dump(score_sheet, fh)
            
            sys.exit()
        except (FileNotFoundError, JSONDecodeError):

            with open("/home/eden/workspace/score_sheet.json", "w",encoding='utf-8') as ff:
                score_sheet = {'wins': 0, 'games': 0, 'average': 0, 'turns': 0}
                json.dump(score_sheet, ff)

            check_winner(turn_counter, status=status)

    wordle = GuessStatus()

    wordle.valid_words = read_file('/home/eden/workspace/accepted_wordle_words.txt')
    wordle.weights = get_weights()


def main():

    layout = [  [sg.Text('Wordle Simulation')],
                [sg.Text("", size=(2, 1), font=("Arial",52),text_color='Black',background_color='Grey', justification='center', key=f'OUTPUT0{num}') for num in range(0, 5)],
                [sg.Text("", size=(2, 1), font=("Arial",52),text_color='Black',background_color='Grey', justification='center', key=f'OUTPUT1{num}') for num in range(0, 5)],
                [sg.Text("", size=(2, 1), font=("Arial",52),text_color='Black',background_color='Grey', justification='center', key=f'OUTPUT2{num}') for num in range(0, 5)],
                [sg.Text("", size=(2, 1), font=("Arial",52),text_color='Black',background_color='Grey', justification='center', key=f'OUTPUT3{num}') for num in range(0, 5)],
                [sg.Text("", size=(2, 1), font=("Arial",52),text_color='Black',background_color='Grey', justification='center', key=f'OUTPUT4{num}') for num in range(0, 5)],
                [sg.Button('Running'), sg.Exit(),sg.Button("Enable"), sg.Button("Disable")]]

    window = sg.Window('Wordle Simulation', layout, no_titlebar=True, resizable=False, size=(480, 800)).Finalize()

    # TODO implement checksum
    WEIGHTS_MD5_CHECKSUM = ''
    #window['Simulation'].update(False)
    sim_run_once = True

    window['Running'].update(disabled=True)
    send = window['Running']

    wordle = GuessStatus()
    wordle.valid_words = read_file('/home/eden/workspace/accepted_wordle_words.txt')
    wordle.weights = get_weights()
    while True:
        event, values = window.Read()
        print(event, values)
        if event in ('Exit'):
            break
        elif event in ('Enable', 'Disable'):
            send.update(disabled=event=='Disable')
            state = 'enabled' if send.Widget['state'] == 'normal' else 'disabled'
            #status.update(f"Button 'SEND' is {state} now.")

        if state == 'enabled':
            if sim_run_once:
                random_int_answer = secrets.randbelow(len(wordle.valid_words))
                sim_answer = wordle.valid_words[random_int_answer]
                sim_run_once = False
            wordle.recommended_answer()
            sim_guess = wordle.best_guess
            sim_status = wordle.check_guess(sim_guess, sim_answer)
            check_winner(wordle.turn_counter, status=sim_status)
            wordle.fill_info(guess=sim_guess, status=sim_status)
            front_end_display(wordle.turn_counter, sim_guess, sim_status)
            wordle.filter_functions()
        else:
            # check if provide answer or simulate game
            # restart all counter and status
            wordle.recommended_answer()
            guess = wordle.best_guess
            print(f'Try {guess}')
            #print guess to try
            print("what was the response")
            #accept input from text box
            status = input()
            check_winner(wordle.turn_counter, status=status)
            wordle.fill_info(guess=guess, status=status)
            wordle.filter_functions()
            guess = wordle.best_guess

        window['OUTPUT00'].update('a', background_color='Green')
        window['OUTPUT33'].update('d', background_color='Red')

        wordle.turn_counter += 1


if __name__ == "__main__":
    main()
