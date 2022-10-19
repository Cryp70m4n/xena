function isJsonObject(strData) {
    try {
        JSON.parse(strData);
    } catch (e) {
        return false;
    }
    return true;
}



let usr = localStorage.getItem('user');
let session = localStorage.getItem('session');


document.getElementById("user").textContent += usr.replaceAll('"', '');


function get_vaults() {
	let method = "POST"
    let action = "/get_vaults"
	let xhr = new XMLHttpRequest();
	xhr.open(method, action, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
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
			vaults_element.style.color = "white";
            return "Success!"
		}
		return "Failure!";
	}

	xhr.send(JSON.stringify(data));
}


function insert_into_vault() {
	let target_vault = document.getElementById("vaultname").value;
	let filename = document.getElementById("filename").value;
	let xhr = new XMLHttpRequest();
	let form = document.getElementById("insert_into_vault");
	xhr.open(form.method, form.action, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	let file = document.getElementById("filedata").files;
	let reader=new FileReader();
	reader.readAsBinaryString(file[0])
	reader.onload = function (e) {
		let filedata = btoa((e.target.result));  
		let data = {
			"user": usr,
			"session": session,
			"target_vault": target_vault,
			"filedata": filedata,
			"filename": filename
		};
		xhr.onload = function() {
			let response = null;
			if (xhr.status >= 200 && xhr.status < 300) {
				response = xhr.responseText;
			}
			if(isJsonObject(response) != true)
				return "Failure!"
			let response_obj = JSON.parse(response);
			if(response_obj.response_code) {
				console.log(response_obj)
				return "Success!";
			}
			return "Failure!";
		}

		xhr.send(JSON.stringify(data));
	}
}

function delete_from_vaults() {
	let target_vault = document.getElementById("vname").value;
	let filename = document.getElementById("fname").value;
	let xhr = new XMLHttpRequest();
	let form = document.getElementById("delete_from_vault");
	xhr.open(form.method, form.action, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	let data = {
		"user": usr,
		"session": session,
		"target_vault": target_vault,
		"filename": filename
	};
	xhr.onload = function() {
		let response = null;
		if (xhr.status >= 200 && xhr.status < 300) {
			response = xhr.responseText;
		}
		if(isJsonObject(response) != true)
			return "Failure!"
		let response_obj = JSON.parse(response);
		if(response_obj.response_code) {
			console.log(response_obj)
			return "Success!";
		}
		return "Failure!";
	}

	xhr.send(JSON.stringify(data));
}