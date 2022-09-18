function submitform() {
	let xhr = new XMLHttpRequest();
	let form = document.getElementById("user_password_form")
	xhr.open(form.method, form.action, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	let usr = document.getElementById("username").value
	let passwd = document.getElementById("password").value    
	let data = {
		"user": usr,
		"password": passwd,
	};
	xhr.onload = function() {
		let response = null
		if (xhr.status >= 200 && xhr.status < 300) {
			response = xhr.responseText;
		}
		let response_obj = JSON.parse(response)
		let token = response_obj.token
		let token_object = {'session': token}
		console.log(token_object)
		localStorage.setItem('token_object', JSON.stringify(token_object));
	}

	xhr.send(JSON.stringify(data));
}