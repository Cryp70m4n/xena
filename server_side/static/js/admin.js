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
	let form = document.getElementById("access");
	xhr.open(form.method, form.action, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	let user = localStorage.getItem('user')
	let session = localStorage.getItem('session')
	console.log(user)
	console.log(session)
	let data = {
		"user": user,
		"session": session
	};
	xhr.onload = function() {
		let response = null;
		if (xhr.status >= 200 && xhr.status < 300) {
			response = xhr.responseText;
		}
		console.log(response)
        document.open();
        document.write(response);
        document.close();
	}

	xhr.send(JSON.stringify(data));
}