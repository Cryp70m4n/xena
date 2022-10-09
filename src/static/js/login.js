function isJsonObject(strData) {
    try {
        JSON.parse(strData);
    } catch (e) {
        return false;
    }
    return true;
}

function submitform() {
	let xhr = new XMLHttpRequest();
	let form = document.getElementById("user_password_form");
	xhr.open(form.method, form.action, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	let usr = document.getElementById("username").value;
	let passwd = document.getElementById("password").value;    
	let data = {
		"user": usr,
		"password": passwd
	};
	xhr.onload = function() {
		let response = null;
		if (xhr.status >= 200 && xhr.status < 300) {
			response = xhr.responseText;
		}
		if(isJsonObject(response) != true)
			return "Failure!"
		let response_obj = JSON.parse(response);
		if(response_obj.token) {
			let token = response_obj.token;
			localStorage.setItem('session', JSON.stringify(token));
			localStorage.setItem('user', JSON.stringify(usr));
			if(usr=="root") {
				window.location.href = "/admin";
			}
			else {
				window.location.href = "/profile";
			}
			return "Success!";
		}
		return "Failure!";
	}

	xhr.send(JSON.stringify(data));
}