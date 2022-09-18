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
	xhr.onreadystatechange = function() {
		if (xhr.readyState === 4) {
			console.log(xhr.response); 
		}
	}

	xhr.send(JSON.stringify(data));
}