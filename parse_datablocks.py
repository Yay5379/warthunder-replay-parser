import os
import re
import sys
import blk.binary as bin
import blk.text as txt
import typing as t
from io import BytesIO

def create_text(name) -> t.TextIO:
    file_path = os.getcwd()
    i = 2
    if os.path.exists(f'{file_path}/{name}.blk'):
        while os.path.exists(f'{file_path}/{name}({i}).blk'):
            i += 1
        return open(f'{file_path}/{name}({i}).blk', 'x')
    else:
        return open(f'{file_path}/{name}.blk', 'x')

def serialize_text(root, ostream):
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

def _parse_datablocks(path):

    magic = re.compile(b'\x01\x20\x01')

    ignored_vehicles = ["dummy_plane"]

    with open(path, 'rb') as f:
        replay = f.read()
    
    for m in magic.finditer(replay):
        try:
            vehicle = _get_text(replay[m.end() + 1:m.end() + 255])

            if len(vehicle) > 2 and vehicle not in ignored_vehicles:
                
                vehicle_len = replay[m.end()]

                weapon_preset_len = replay[m.end() + vehicle_len + 1]

                skin_len = replay[m.end() + vehicle_len + weapon_preset_len + 2]

                datablock_magic = replay[m.end() + vehicle_len + weapon_preset_len + skin_len + 5]

                if datablock_magic == 1:
                    print(f"parsing {vehicle}")
                    # idk how to make this read the actual datablock size but it still works
                    datablock = BytesIO(replay[m.end() + vehicle_len + weapon_preset_len + skin_len + 5:m.end() + 8192])
                    with datablock as istream:
                        try:
                            root = bin.compose_fat(istream)
                            with create_text(vehicle) as ostream:
                                serialize_text(root, ostream)
                        except:
                            raise
        except:
            raise

def main():
    file = os.path.abspath(sys.argv[1])
    
    print(f"parsing replay in {file}")

    _parse_datablocks(file)

if __name__ == "__main__":
    main()
