function isJsonObject(strData) {
    try {
        JSON.parse(strData);
    } catch (e) {
        return false;
    }
    return true;
}


let usr = localStorage.getItem('user');

document.getElementById("user").textContent += usr.replaceAll('"', '');


function get_vaults() {
	let method = "POST"
    let action = "/get_vaults"
	let xhr = new XMLHttpRequest();
	xhr.open(method, action, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	let session = localStorage.getItem('session');
	let data = {
		"user": usr,
		"session": session
	};
	xhr.onload = function() {
		let response = null;
		if (xhr.status >= 200 && xhr.status < 300) {
			response = xhr.responseText;
		}
		if(isJsonObject(response) != true)
			return "Failure!"
		let response_obj = JSON.parse(response);
		if(response_obj.vaults) {
            let vaults = response_obj.vaults;
            let vaults_element = document.getElementById("vaults");
            vaults_element.textContent += vaults;
            vaults_element.textContent += " ";
            return "Success!"
		}
		return "Failure!";
	}

	xhr.send(JSON.stringify(data));
}
