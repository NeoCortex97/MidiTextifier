#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mido
import argparse
import sys
import os
from operator import itemgetter


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


def get_arguments():
    parser = argparse.ArgumentParser(description="Convert midi files to chat commands")
    parser.add_argument("-f", "--file", dest="file", required=True,
                        type=lambda x: is_valid_file(parser, x),
                        help="Specifies the file to be converted.")
    parser.add_argument("-i", "--instrument", dest="instrument", default="piano",
                        choices=["piano", "guitar", "brass", "organ", "vibes"],
                        help="Specifies what instrument you want to use. Defaults to piano.")
    parser.add_argument("-t", "--track", dest="track", default=0, type=int,
                        help="Specifies the index of the track to be converted.")
    parser.add_argument("-s", "--stats", dest="stats", action='store_true',
                        help="Print file stats instead of converting.")
    parser.add_argument("-a", "--all", dest="all", action="store_true",
                        help="Convert all tracks to text.")
    return parser.parse_args()


def print_stats(file: mido.MidiFile):
    print("File name:        {}".format(file.filename))
    print("File type:        {}".format(["single", "sync", "async"][file.type]))
    print("{}".format(str(file.length) + "s" if file.type < 2 else "unknown"))
    print("Number of tracks: {}".format(len(file.tracks)))
    print("Tracks:")
    for index, track in enumerate(file.tracks):
        print("    {} {}".format(index, track.name if track.name != "" else "META"))


def convert_track_to_text(track: mido.MidiTrack,  instrument: str, tpb: int):
    active_notes = {}
    current_ticks = 0
    result = []
    index = 0

    for note in track:
        if note.type == 'note_on' and note.velocity > 0:
            if -1 in active_notes.keys():
                tmp_pause = active_notes[-1]
                tmp_pause["end"] = current_ticks
                result.append(tmp_pause)
                del active_notes[-1]
            if note.note not in active_notes.keys():
                active_notes[note.note] = {"start": current_ticks, "idx": index,
                                           "text": convert_note_to_text(note.note)}
                index += 1
        elif note.type == 'note_off' or (note.type == 'note_on' and note.velocity == 0):
            if note.note in active_notes.keys():
                tmp_note = active_notes[note.note]
                tmp_note["end"] = current_ticks
                result.append(tmp_note)
                del active_notes[note.note]
                if len(active_notes.keys()) == 0:
                    active_notes[-1] = {"start": current_ticks, "idx": index, "text": "p"}
                    index += 1
        current_ticks += note.time

    if len(result) == 0:
        print("The currently selected track contains no playable notes!")
        return ""

    for n in result:
        try:
            tmp_val = round((tpb * 4) / n["end"] - n["start"])
            n["duration"] = min([1, 2, 4, 8, 16], key=lambda x: abs(x - tmp_val))
        except ZeroDivisionError:
            pass

    sorted_result = sorted(result, key=itemgetter('idx'))  # ensure items are sorted
    tmp = []
    for item in result:
        if "duration" in item.keys():
            if item["duration"] != 4:
                tmp.append("{}{}".format(item["text"], item["duration"]))
            else:
                tmp.append("{}".format(item["text"]))
    return str(instrument) + " " + " ".join(tmp)


if __name__ == '__main__':
    args = get_arguments()
    file = mido.MidiFile(args.file)
    if args.stats:
        print_stats(file)
    elif args.all:
        for track in file.tracks:
            print(track.name if track.name != "" else "META")
            print("  " + convert_track_to_text(track, args.instrument, file.ticks_per_beat))
    else:
        print(convert_track_to_text(file.tracks[args.track], args.instrument, file.ticks_per_beat))
