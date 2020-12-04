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
            let tmp = toNotes(events);
            const name = tmp[0];
            console.log(name);
            let notes = tmp[1]; 
            let ticks = 0;
            let activeNotes = {};
            let finishedNotes = [];
            var trackString = "";
            notes.forEach(element => {
                if(element.type === "noteon"){
                    if(activeNotes[-1]){
                        let pause = activeNotes[-1];
                        pause.duration = ticks - pause.start;
                        finishedNotes.push(pause);
                        delete activeNotes[-1];
                    }
                    element.start = ticks;
                    if(Object.keys(activeNotes).length == 0)
                        activeNotes[element.note] = element;
                }
                else if(activeNotes[element.note]){
                    let note = activeNotes[element.note];
                    note.duration = ticks - note.start;
                    finishedNotes.push(note);
                    delete activeNotes[element.note];
                    if (Object.keys(activeNotes).length === 0) {
                        activeNotes[-1] = {
                            start: ticks,
                            type: "pause"
                        }
                    }
                }
                ticks += element.ticks;
            });
            finishedNotes.forEach((element) => {
                const r = noteToString(element, midiFile.header.getTicksPerBeat())
                trackString += r === "" ? "" : "&nbsp;" + r;
            });
            if (trackString !== "") {
                outContainer.innerHTML += "<li><h2>" + name + "</h2>" + trackString + "</li>";
            }
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
    let name = "";
    events.forEach((evt) => {
        if (evt.type === MIDIEvents.EVENT_META && evt.subtype === MIDIEvents.EVENT_META_TRACK_NAME) {
            name = String.fromCharCode.apply(null, evt.data);
        }
        if (evt.type === MIDIEvents.EVENT_MIDI) {
            if (evt.subtype === MIDIEvents.EVENT_MIDI_NOTE_ON && evt.param2 > 0) {
                notes.push({
                    type: "noteon",
                    note: evt.param1,
                    velocity: evt.param2,
                    ticks: evt.delta,
                    hts: evt.param1 % 12,
                    octave: parseInt(evt.param1 / 12),
                    channel: evt.channel
                });
            }else if (evt.subtype === MIDIEvents.EVENT_MIDI_NOTE_OFF || 
                     (evt.subtype === MIDIEvents.EVENT_MIDI_NOTE_ON && evt.param2 === 0)) {
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
    console.log([name, notes]);
    return [name, notes];
}

function noteToString(element, tpb){
    let res = "";
    if (element.type === "noteon"){
        const hts = ['c{}', 'c{}#', 'd{}', 'd{}#', 'e{}', 'f{}', 'f{}#', 'g{}', 'g{}#', 'a{}', 'a{}#', 'h{}'];
        const octaves = ["'''", "''", "'", "", "", "'", "''", "'''"];
        if(element.note > 47){
            res = hts[element.hts].replace('{}', octaves[element.octave]);
        }
        else{
            res = hts[element.hts].replace('{}', octaves[element.octave]).toUpperCase();
        }
    }
    else{
        res = "p";
    }
    let length = parseInt((tpb * 4) / element.duration);
    if(!isNaN(length) && length !== 0)
        return res + (length === 4 ? "" : !(length > 32) ? length : "32");
    else
        return "";
}

function dropHandler(ev) {
    console.log('File(s) dropped');

  // Prevent default behavior (Prevent file from being opened)
  ev.preventDefault();

  if (ev.dataTransfer.items) {
    // Use DataTransferItemList interface to access the file(s)
    for (var i = 0; i < ev.dataTransfer.items.length; i++) {
      // If dropped items aren't files, reject them
      if (ev.dataTransfer.items[i].kind === 'file') {
        var file = ev.dataTransfer.items[i].getAsFile();
        console.log('... file[' + i + '].name = ' + file.name);
      }
    }
  } else {
    // Use DataTransfer interface to access the file(s)
    for (var i = 0; i < ev.dataTransfer.files.length; i++) {
      console.log('... file[' + i + '].name = ' + ev.dataTransfer.files[i].name);
    }
  }
}

function dragOverHandler() {
    
}