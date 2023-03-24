function autoDuration() {
    let notes_string = document.getElementById('notes_string').value;
    let notes = notes_string.split(' ');
    let durations = {};
    for (let note of notes) {
      let pitch, duration;
      if (note.includes('(')) {
        pitch = note.slice(0, note.indexOf('('));
        duration = note.slice(note.indexOf('(') + 1, note.indexOf(')'));
      } else {
        pitch = note;
        duration = '1/4';
      }
      durations[pitch] = duration;
    }
    let new_notes = '';
    for (let note of notes) {
      let pitch, duration;
      if (note.includes('(')) {
        pitch = note.slice(0, note.indexOf('('));
        duration = note.slice(note.indexOf('(') + 1, note.indexOf(')'));
      } else {
        pitch = note;
        duration = durations[pitch];
      }
      new_notes += pitch + '(' + duration + ') ';
    }
    document.getElementById('notes_string').value = new_notes.trim();
  }
  
  function toggleAutoDuration() {
    let noteDurationSelect = document.getElementById('note_duration');
    let autoDurationButton = document.getElementById('auto_duration');
  
    if (autoDurationButton.classList.contains('active')) {
      autoDurationButton.classList.remove('active');
      noteDurationSelect.disabled = false;
    } else {
      autoDurationButton.classList.add('active');
      noteDurationSelect.disabled = true;
      autoDuration();
    }
  }
  
  $(document).ready(function() {
    $('#root_note, #note_duration').change(function() {
      let rootNote = $('#root_note').val();
      let noteDuration = $('#note_duration').val();
      let exampleText = rootNote + '4(' + noteDuration + ')';
      $('#notes_string').val(exampleText);
    });
  
    $('button#auto_duration').click(function() {
      toggleAutoDuration();
    });
  
    $('#note_duration').change(function() {
      if (!document.getElementById('auto_duration').classList.contains('active')) {
        let noteDuration = $('#note_duration').val();
        let notes_string = document.getElementById('notes_string').value;
        let notes = notes_string.split(' ');
        let new_notes = '';
  
        for (let note of notes) {
          let pitch;
          if (note.includes('(')) {
            pitch = note.slice(0, note.indexOf('('));
          } else {
            pitch = note;
          }
          new_notes += pitch + '(' + noteDuration + ') ';
        }
  
        document.getElementById('notes_string').value = new_notes.trim();
      }
    });
  });
  