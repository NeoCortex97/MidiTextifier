#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

import mido
import pathlib
import argparse
import sys
import os


def convert_note_to_text(note: int):
    hts = ['c{}', 'c{}#', 'd{}', 'd{}#', 'e{}', 'f{}', 'f{}#', 'g{}', 'g{}#', 'a{}', 'a{}#', 'h{}']
    octaves = ["'''", "''", "'", "", "", "'", "''", "'''"]
    half_tone = note % 12
    octave = note // 12
    result = hts[half_tone].format(octaves[octave])
    if note <= 47:
        return result.upper()
    return result


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert midi files to chat commands")
    parser.add_argument("-f", "--file",
                        dest="file",
                        required=True,
                        type=lambda x: is_valid_file(parser, x),
                        help="Specifies the file to be converted.")
    parser.add_argument("-i", "--instrument",
                        dest="instrument",
                        default="piano",
                        choices=["piano", "guitar", "brass", "organ", "vibes"],
                        help="Specifies what instrument you want to use. Defaults to piano.")
    parser.add_argument("-t", "--track",
                        dest="track",
                        default=0,
                        type=int,
                        help="Specifies the track to be converted")
    parser.add_argument("-s", "--stats",
                        dest="stats",
                        default=False,
                        type=bool,
                        help="Print file stats instead of converting.")

    args = parser.parse_args()
    if args.stats:
        pass
    else:
        # Process all note on messages
        file = mido.MidiFile(args.file)
        active_notes = {}
        current_ticks = 0
        result = []
        index = 0

        # sys.stdout.write(args.instrument + " ")
        for note in file.tracks[args.track]:
            if note.type == 'note_on' and note.velocity > 0:
                if note.note not in active_notes.keys():
                    active_notes[note.note] = {"start": current_ticks, "idx": index,  "text": convert_note_to_text(note.note)}
                    index += 1
                # sys.stdout.write(convert_note_to_text(note.note) + " ")
                # sys.stdout.flush()
            elif note.type == 'note_off' or (note.type == 'note_on' and note.velocity == 0):
                if note.note in active_notes.keys():
                    tmp_note = active_notes[note.note]
                    tmp_note["end"] = current_ticks
                    result.append(tmp_note)
                    del active_notes[note.note]
            current_ticks += note.time

        if len(result) == 0:
            print("The currently selected track contains no playable notes!")

        # sys.stdout.write("\n")
        for n in result:
            n["duration_ticks"] = n["end"] - n["start"]
            n["duration"] = round((file.ticks_per_beat * 4) / n["duration_ticks"])
            print(n)
