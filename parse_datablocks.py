import os
import re
import sys
import blk.binary as bin
import blk.text as txt
import typing as t
from io import BytesIO

def create_text(name:str, uid:int) -> t.TextIO:
    file_path = os.getcwd()
    if os.path.exists(f'{file_path}/{name}({uid}).blk'):
        return open(f'{file_path}/{name}({uid}).blk', 'a')
    else:
        return open(f'{file_path}/{name}({uid}).blk', 'x')

def serialize_text(root, ostream, data):
    if root is None:
        print(data, file=ostream)
    else:
        print(data, file=ostream)
        txt.serialize(root, ostream, dialect=txt.StrictDialect)

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

def parse_datablocks(path):

    magic = re.compile(b'\x01\x20\x01')

    ignored_vehicles = ["dummy_plane"]

    with open(path, 'rb') as f:
        replay = f.read()
    
    for m in magic.finditer(replay):
        try:
            vehicle = _get_text(replay[m.end() + 1:m.end() + 255])

            if len(vehicle) > 2 and vehicle not in ignored_vehicles:

                unit_id = replay[m.start() - 4]
                
                vehicle_len = replay[m.end()]

                weapon_preset_len = replay[m.end() + vehicle_len + 1]

                weapon_preset = _get_text(replay[m.end() + len(vehicle) + 2:m.end() + 255]) if weapon_preset_len > 0 else "default"

                skin_len = replay[m.end() + vehicle_len + weapon_preset_len + 2]

                skin = _get_text(replay[m.end() + len(vehicle) + len(weapon_preset) + 3:m.end() + 255]) if skin_len > 0 else "default"

                datablock_magic = replay[m.end() + vehicle_len + weapon_preset_len + skin_len + 5]

                if len(skin) != skin_len and skin != "default":
                    skin = skin.rstrip(skin[-1])

                if datablock_magic == 1:
                    print(f"parsing {vehicle}({unit_id})")
                        
                    unit_data=(
                    f'unit_id:i={unit_id}\n'
                    f'vehicle:t="{vehicle}"\n'
                    f'weapon_preset:t="{weapon_preset}"\n'
                    f'skin:t="{skin}"'
                    )

                    # idk how to make this read the actual datablock size but it still works
                    datablock = BytesIO(replay[m.end() + vehicle_len + weapon_preset_len + skin_len + 5:m.end() + 2048])

                    with datablock as istream:
                        try:
                            root = bin.compose_fat(istream)
                            with create_text(vehicle, unit_id) as ostream:
                                serialize_text(root, ostream, unit_data)
                        except:
                            pass
                else:
                    print(f"parsing {vehicle}({unit_id})")

                    unit_data=(
                    f'unit_id:i={unit_id}\n'
                    f'vehicle:t="{vehicle}"\n'
                    f'weapon_preset:t="{weapon_preset}"\n'
                    f'skin:t="{skin}"'
                    )

                    with create_text(vehicle, unit_id) as ostream:
                        serialize_text(None, ostream, unit_data)
        except:
            pass

def parse_streaks(path):

    magic = re.compile(b'\x02\x58\x78\xf0')

    with open(path, 'rb') as f:
        replay = f.read()
    
    for m in magic.finditer(replay):
        try:
            streak_id = replay[m.end()]

            player_id = replay[m.end() + 3]

            streak_name = _get_text(replay[m.end() + 8:m.end() + 255])

            streak_data=(
                f'streak:t="{streak_name}"\n'
                f'streak_id:i={streak_id}\n'
            )

            with create_text('streak_data', player_id) as ostream:
                serialize_text(None, ostream, streak_data)
        except:
            pass

def main():
    file = os.path.abspath(sys.argv[1])

    print(f"parsing replay in {file}")

    parse_datablocks(file)
    parse_streaks(file)

if __name__ == "__main__":
    main()
