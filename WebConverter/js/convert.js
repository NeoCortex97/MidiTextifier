document.getElementById("convert").addEventListener("click", function (evt) {
    const file = document.getElementById("midiFile").files[0];
    const reader = new FileReader();

    reader.onload = (result) => {
        const data = result.target.result;
        const midiFile = new MIDIFile(data);
        const outContainer = document.getElementById("outputContainer");
        outContainer.innerHTML = "";
        for(var track = 0; track < midiFile.header.getTracksCount(); ++track){
            const events = midiFile.getTrackEvents(track);
            let notes = toNotes(events);
            notes.forEach(element => {
                try{
                    outContainer.innerHTML += noteToString(element) + "&nbsp;";
                }
                catch(e){
                    console.log(element);
                    console.log(e);
                }
            });
            outContainer.innerHTML += "<br/>";
        };
    };
    reader.onerror = (err) => {
        console.log(err);
        alert(err);
    };
    reader.readAsArrayBuffer(file);
});

function toNotes(events) {
    let notes = [];
    events.forEach((evt) => {
        if (evt.type === MIDIEvents.EVENT_MIDI) {
            if (evt.subtype === MIDIEvents.EVENT_MIDI_NOTE_ON) {
                if (evt.param1 == undefined) {
                    console.log(evt);
                }
                notes.push({
                    type: "noteon",
                    note: evt.param1,
                    velocity: evt.param2,
                    ticks: evt.delta,
                    hts: evt.param1 % 12,
                    octave: parseInt(evt.param1 / 12),
                    channel: evt.channel
                });
            }else if (evt.subtype === MIDIEvents.EVENT_MIDI_NOTE_OFF) {
                if (evt.param1 == undefined) {
                    console.log(evt);
                }
                notes.push({
                    type: "noteoff",
                    note: evt.param1,
                    velocity: evt.param2,
                    ticks: evt.delta,
                    hts: evt.param1 % 12,
                    octave: parseInt(evt.param1 / 12),
                    channel: evt.channel
                });
            }
        }
    });
    return notes;
}

function noteToString(element){
    const hts = ['c{}', 'c{}#', 'd{}', 'd{}#', 'e{}', 'f{}', 'f{}#', 'g{}', 'g{}#', 'a{}', 'a{}#', 'h{}'];
    const octaves = ["'''", "''", "'", "", "", "'", "''", "'''"];
    return hts[element.hts].replace('{}', octaves[element.octave])
}