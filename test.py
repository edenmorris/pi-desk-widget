import PySimpleGUI as sg

sg.theme("DarkBlue3")
sg.set_options(font=("Courier New", 12))

layout = [
    [sg.Button("SEND")],
    [sg.Button("Enable"), sg.Button("Disable")],
    [sg.StatusBar("Button 'SEND' is enabled now.", size=(30, 1), key='STATUS')],
]
window = sg.Window('Title', layout, finalize=True)
send, status = window['SEND'], window['STATUS']
while True:

    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event in ('Enable', 'Disable'):
        send.update(disabled=event=='Disable')
        state = 'enabled' if send.Widget['state'] == 'normal' else 'disabled'
        status.update(f"Button 'SEND' is {state} now.")

    if state == 'disabled':
        print('disabled')
    else:
        print('enable')

window.close()