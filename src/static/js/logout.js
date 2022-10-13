function logout() {
    let usr = localStorage.getItem('user');
    let sess = localStorage.getItem('session');
	let endpoint = "/logout"
    let method = "POST"
	let xhr = new XMLHttpRequest();
	xhr.open(method, endpoint, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	let data = {
        "user": usr,
        "session": sess,
	};
	xhr.onload = function() {
		let response = null;
		if (xhr.status >= 200 && xhr.status < 300) {
			response = xhr.responseText;
		}
		if(isJsonObject(response) != true)
			return "Failure!"
		let response_obj = JSON.parse(response);
        if(response_obj.response_code == -1) {
            localStorage.removeItem("user")
            localStorage.removeItem("session")
            window.location.href = "/";
            return "Logout!"
        }
		if(response_obj.response_status) {
            console.log(response_obj)
		}
		return "Failure!";
	}

	xhr.send(JSON.stringify(data));
}