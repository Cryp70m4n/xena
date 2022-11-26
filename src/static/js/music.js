function isJsonObject(strData) {
    try {
        JSON.parse(strData);
    } catch (e) {
        return false;
    }
    return true;
}

function music() {
    let method = "POST"
    let action = "/music_choice"
    let xhr = new XMLHttpRequest();
    xhr.open(method, action, true);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.onload = function() {
        let response = null;
        if (xhr.status >= 200 && xhr.status < 300) {
            response = xhr.responseText;
        }
        if(isJsonObject(response) != true)
            return "Failure!"
        let response_obj = JSON.parse(response);
        console.log(response_obj)
        if(response_obj.song) {
            let songName = `<p id="songName">${response_obj.song}</p>`
            let html = `<audio id="song" src="${"/static/music/"+response_obj.song}" controls></audio>`
            let song = document.getElementById("load")
            song.innerHTML = songName;
            song.innerHTML += html;
            return "Success!";
        }
        return "Failure!";
    }

    xhr.send();
}

function next() {
    document.getElementById("load").innerHTML = "";
    music();
}


music();