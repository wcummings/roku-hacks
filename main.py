import time
import random
import inquirer
from rokussdpprotocol import RokuSSDPProtocol
from showdefinition import ShowDefintition


DOWN_KEY = "Down"
ENTER_KEY = "Select"
LEFT_KEY = "Left"

SHOWS = [
    ShowDefintition("king of the hill", "hulu", 13, 24),
    ShowDefintition("seinfeld", "netflix", 9, 24),
    ShowDefintition("community", "hulu", 6, 24),
    ShowDefintition("malcom in the middle", "hulu", 7, 24)
]


if __name__ == '__main__':
    protocol = RokuSSDPProtocol()
    protocol.search_for_devices_n_times(1)
    protocol.search_devices_until_one_found()
    device_map = protocol.get_devices()
    questions = [
        inquirer.List('device',
            message="Select a device",
            choices=device_map.keys())
        ]
    answers = inquirer.prompt(questions)
    selected_device_name = answers['device']
    show_def = random.choice(SHOWS)
    show_name = show_def.name
    app = show_def.provider
    print("Chose {}".format(show_name))
    print("Launching...")
    protocol.launch(selected_device_name, show_name, app)
    time.sleep(30)
    print("A C T I V A T I N G")
    protocol.keypress(selected_device_name, LEFT_KEY)
    time.sleep(.5)
    for n in range(random.randint(0, show_def.no_seasons)):
        protocol.keypress(selected_device_name, DOWN_KEY)
        time.sleep(.5)
    protocol.keypress(selected_device_name, ENTER_KEY)
    for n in range(random.randint(0, show_def.no_episodes_per_season)):
        protocol.keypress(selected_device_name, DOWN_KEY)
        time.sleep(.5)
    protocol.keypress(selected_device_name, ENTER_KEY)
