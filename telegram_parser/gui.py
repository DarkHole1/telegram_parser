import os
import PySimpleGUI as sg
from main import main


sg.theme('DarkBlue') 

def linear_setup_window(window_name, init_setup):
    if init_setup == 1:
        layout = [[sg.Text("How many letters in the link might be (at least 5): "), sg.Input(size=(3, 1), key="num_letters_init"), sg.Button('Ok', enable_events=True, key = 'get_length')],
                  [sg.Exit(tooltip='Exit only if the button "OK changed to "Done" or if you won\'t use Linear Parse Mode!!!')]
                  ]
    else:
        layout = [[sg.Text("Do you want to change number of letters in link? "), sg.Button('Yes', enable_events=True, key = 'update_length_text'), sg.Button('No', enable_events=True, key = 'Exit_no')],
                  [[sg.Text("How many letters in the link might be (at least 5): "), sg.Input(size=(3, 1), key="num_letters_init", disabled=True), sg.Button('Ok', enable_events=True, key = 'get_length', disabled=True)],
                  [sg.Exit()]
                  ]]
    window = sg.Window(window_name, layout, modal=True) 
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED or event == 'Exit_no':
            break
        if event == 'get_length':
            start_point = 'a' + '1'*(int(values['num_letters_init'])-1)
            open('.last_link', 'w').write(start_point)
            window['get_length'].Update(visible=False)
        if event == 'update_length_text':
            window['num_letters_init'].update(disabled=False)
            window['get_length'].update(disabled=False)
    window.close()
    

def mutation_setup_window():
    try:
        os.remove('mutated')
    except FileNotFoundError:
        pass
    layout = [[sg.Text("Input initial word to mutate (length of the word is greater than 5 letters): ")], 
              [sg.Input(size=(32, 1), key="word_init"), sg.Button('Ok', enable_events=True, key = 'get_mutated_word')],
              [sg.Button('Exit', tooltip='Exit only if the button "OK changed to "Done" or if you won\'t use Mutation Parse Mode!!!',key='Exit_no', enable_events=True) ]
                  ] 
    window = sg.Window('Mutation Setup', layout, modal=True) 
    while True:
        event, values = window.read()
        if event == 'get_mutated_word':
            mutated_initial_link = values['word_init']
            window['get_mutated_word'].update('Done')
        if event == "Exit" or event == sg.WIN_CLOSED or event == 'Exit_no':
            window.close()
            return mutated_initial_link
    window.close()
    
        
    
def main_window():
    layout_main = [ 
    [sg.HorizontalSeparator()],
    [sg.Text("=== Work mode ===", justification='center',size=(70,1))],
    [sg.HorizontalSeparator()],
    [sg.Text("Choose content to parse: ")], 
                     [sg.Checkbox('Channels', key='channel_content'), 
                     sg.Checkbox('Groups', key='group_content'), 
                     sg.Checkbox('Users', key='user_content'), 
                     sg.Checkbox('Stickers', key='stickers_content'), 
                     sg.Checkbox('Bots', key='bots_content')],
    [sg.Text("Choose parsing mode: "), sg.Listbox(values=['Linear','Random','Mutation'], size=(20, 3), key='parsing_mode_list', enable_events=True)],
    [sg.Text("Turbo mode: "), sg.Checkbox('', key='turbo_mode')],
    [sg.HorizontalSeparator()],
    [sg.Text("=== Output mode ===", justification='center',size=(70,1))],
    [sg.HorizontalSeparator()],
    [sg.Text("Choose output mode: "), sg.Listbox(values=['All output','If something found','Disabled'], size=(20, 3), key='output_mode_list')],
    [sg.HorizontalSeparator()],
    [sg.Text("=== Write mode ===", justification='center',size=(70,1))],
    [sg.HorizontalSeparator()],
    [sg.Text("Only addresses mode: "), sg.Checkbox('', key='fast_mode')],
    [sg.Button('Run', key='start_program', enable_events=True), sg.Button('Stop', key='stop_program', enable_events=True)], 
    [sg.Multiline(size=(70, 25), key='Output')]    
    ]

    window = sg.Window("TP - Telegram Parser", layout_main, finalize=True)
    try:
        mutated_initial_link = None
        while True:
            event, values = window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            if event == "parsing_mode_list":
                if values['parsing_mode_list'][0] == 'Linear':
                    try:                                    # LINK Checking
                        open('.last_link').read()
                        window_name = 'Linear Parsing Setup'
                        init_setup = 0
    
                    except FileNotFoundError:
                        window_name = 'Linear Parsing Initial Setup'
                        init_setup = 1
                    linear_setup_window(window_name, init_setup)
                
                if values['parsing_mode_list'][0] == 'Mutation':
                    mutated_initial_link = mutation_setup_window()
                
            if event == 'start_program':
                if values['parsing_mode_list'][0] == 'Linear':
                    work_mode = '1'
                elif values['parsing_mode_list'][0] == 'Random':
                    work_mode = '2'
                elif values['parsing_mode_list'][0] == 'Mutation':
                    work_mode = '3'
                    
                parser_type = ''
                if values['channel_content'] == True:
                    parser_type += '2'
                if values['group_content'] == True:
                    parser_type += '3'
                if values['user_content'] == True:
                    parser_type += '4'
                if values['stickers_content'] == True:
                    parser_type += '5'
                if values['bots_content'] == True:
                    parser_type += '6'
                
                if values['turbo_mode'] == True:
                    turbo_mode = True
                else:
                    turbo_mode = False
                
                if values['fast_mode'] == True:
                    fast_mode = True
                else:
                    fast_mode = False
                    
                
                if values['output_mode_list'][0] == 'All output':
                    output = '1'
                    print = window['Output'].print
                elif values['output_mode_list'][0] == 'If something found':
                    output = '2'
                    print = window['Output'].print
                elif values['output_mode_list'][0] == 'Disabled':
                    output = '3'
                    window['Output'].Update(visible=False)
                    print = print
                
                main(work_mode, parser_type, window, turbo_mode, fast_mode, output, print, mutated_initial_link)
        window.close()
    except AttributeError:
        print('Fuck')
        # window.close()
if __name__ == "__main__":
    main_window()