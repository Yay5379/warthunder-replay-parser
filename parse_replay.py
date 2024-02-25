import os
import re
import sys
from datetime import datetime
import json

def parse_replay(folder):
    """
    parse a replay which is stored in a folder
    Assumes "folder" is a directory with replay files 0000.wrpl, 0001.wrpl ...
    """

    replay_files = _get_files(folder)

    units = []
    for file in replay_files:
        print(f"parsing {file}")
        units += _parse_replay_file(file)
    
    # join the unit ids
    units2 = []

    for uid in set([u["unit_id"] for u in units]):
        vehicles = []
        for v in list(set([u["vehicle"] for u in units if u["unit_id"] == uid])):
            for w in list(set([u["weapon_preset"] for u in units if u["unit_id"] == uid and u["vehicle"] == v])):
                for s in list(set([u["skin"] for u in units if u["unit_id"] == uid and u["vehicle"] == v])):
                    vehicles.append(
                    {
                        "vehicle": v,
                        "weapon_preset": w,
                        "skin" : s,
                        "num_appearances": len([u for u in units if u["unit_id"] == uid and u["vehicle"] == v])
                    }
            )
        units2.append({
            "unit_id" : uid,
            "vehicles": vehicles,
            "num_appearances": len([p for p in units if p["unit_id"] == uid])
        })

    data = _get_metadata(folder)
    data['num_players'] = len(units2)
    data['units'] = units2

    return data

def _get_text(bstring, letters=None):
    """
    from a binary string, return a text string where only the allowed letters are in
    """

    if letters is None:
        letters = list(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_")

    text = ""
    idx = 0
    while (letter := bstring[idx]) in letters and idx < len(bstring):
        text += chr(letter)
        idx += 1

    return text

def _get_metadata(folder):
    """
    get the metadata from the replay files
    """

    replay_file = os.path.join(folder, "0000.wrpl")
    with open(replay_file, 'rb') as f:
        replay = f.read()

    dir_letters = list(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_/.")

    # level can be found at the position 0x8 to 0x87
    level = _get_text(replay[0x8:0x88], letters=dir_letters)

    # mission file can be found at position 0x88 to 0x18b
    mission_file = _get_text(replay[0x88:0x18c], letters=dir_letters)

    # mission name can be found at position 0x18c to 0x20b
    mission_name = _get_text(replay[0x18c:0x20c])

    # time of day can be found at position 0x20c to 0x28b
    time_of_day = _get_text(replay[0x20c:0x28c])

    # wheather cna be found at position 0x28c to 0x2af
    weather = _get_text(replay[0x28c:0x2b0])

    # time of battle can be found at position 0x388 to 0x38b
    time_of_battle_ts = int.from_bytes(replay[0x388:0x38c], byteorder='little')
    time_of_battle = datetime.fromtimestamp(time_of_battle_ts).strftime('%Y-%m-%d %H:%M:%S')

    return {
        "level" : level,
        "mission_file" : mission_file,
        "mission_name" : mission_name,
        "time_of_day" : time_of_day,
        "weather" : weather,
        "time_of_battle_ts" : time_of_battle_ts,
        "time_of_battle" : time_of_battle,
    }


def _get_files(folder):
    """
    get the replay files
    """

    dirfiles = [os.path.join(folder, f) for f in os.listdir(folder)]

    # Currently we are only looking for files like 0000.wrpl, 0001.wrpl ...
    # (this is how https://warthunder.com/en/tournament/replay/ names replays)
    files_match = ".*\d\d\d\d.wrpl$"

    files = sorted([os.path.abspath(f) for f in dirfiles if re.search(files_match, f)])

    return files


def _parse_replay_file(path):
    """
    parse a single replay files and return instances of vehicles
    """

    # allowed letters for vehicle names
    # letters = list(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_")

    # magic which preceds vehicles
    magic = re.compile(b'\x01\x20\x01')

    # vehicles which are not player vehicles
    ignored_vehicles = ["dummy_plane"]

    with open(path, 'rb') as f:
        replay = f.read()
        
    units = []

    # find all magics in the replay file
    for m in magic.finditer(replay):
        
        # the byte before a name string determines its length so 255 is the max length 
        name_max_len = 255

        try:
            vehicle = _get_text(replay[m.start() + 4:m.start() + name_max_len])
        
            # only if the vehicle name is at least 2 letters, it is actually not garbage
            if len(vehicle) > 2 and vehicle not in ignored_vehicles:

                # player id can be found at the position m.start() - 4
                unit_id = replay[m.start() - 4]

                weapon_preset_len = replay[m.start() + len(vehicle) + 4]

                weapon_preset = _get_text(replay[m.start() + len(vehicle) + 5:m.start() + name_max_len]) if weapon_preset_len > 0 else "default"

                skin_len = replay[m.start() + len(vehicle) + len(weapon_preset) + 5]

                skin = _get_text(replay[m.start() + len(vehicle) + len(weapon_preset) + 6:m.start() + name_max_len]) if skin_len > 0 else "default"

                if len(skin) != skin_len and skin is not "default":
                    skin = skin.rstrip(skin[-1])

                units.append({"unit_id" : unit_id, "vehicle" : vehicle, "weapon_preset" : weapon_preset, "skin" : skin})
        except:
            print(skin_len)
            raise
    
    return units


def main():

    # if we have an argument, use this as path, otherwise use current folder
    try:
        folder = os.path.abspath(sys.argv[1])
    except:
        folder = os.getcwd()

    print(f"parsing replay in {folder}")

    data = parse_replay(folder)

    folder_name = "test"
    file_path = os.getcwd()
    with open(f'{file_path}/{folder_name}.json', 'x') as ostream:
        json.dump(data, ostream, indent=2, separators=(',',':'))

    print()
    print(json.dumps(data, indent=2, separators=(',',':')))

if __name__ == "__main__":
    main()