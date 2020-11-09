#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mido

mid = mido.MidiFile()
track = mido.MidiTrack()
mid.tracks.append(track)

for number in range(0, 96):
    track.append(mido.Message(type="note_on", note=number, velocity=64, time=480))
    track.append(mido.Message(type="note_off", note=number, velocity=0, time=480))

mid.save("Midi/test.mid")
