// BEGINNING OF FRONTEND

function deleteAccount() {    
    const daModal = document.getElementById("daModal");
    const daBtn = document.getElementById("daBtn");
    const span = document.getElementsByClassName("close")[0];

    daBtn.onclick = function() {
        daModal.style.display = "block";
    }

    span.onclick = function() {
        daModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == daModal) {
            daModal.style.display = "none";
        }
    }
}

function createVault() {
    const cvModal = document.getElementById("cvModal");
    const cvBtn = document.getElementById("cvBtn");
    const span = document.getElementsByClassName("close")[1];

    cvBtn.onclick = function() {
        cvModal.style.display = "block";
    }

    span.onclick = function() {
        cvModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == cvModal) {
            daModal.style.display = "none";
        }
    }
}

function deleteVault() {
    const dvModal = document.getElementById("dvModal");
    const dvBtn = document.getElementById("dvBtn");
    const span = document.getElementsByClassName("close")[2];

    dvBtn.onclick = function() {
        dvModal.style.display = "block";
    }

    span.onclick = function() {
        dvModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == dvModal) {
            dvModal.style.display = "none";
        }
    }
}

function changePermissionLevel() {
    const cplModal = document.getElementById("cplModal");
    const cplBtn = document.getElementById("cplBtn");
    const span = document.getElementsByClassName("close")[3];

    cplBtn.onclick = function() {
        cplModal.style.display = "block";
    }

    span.onclick = function() {
        cplModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == cplModal) {
            cplModal.style.display = "none";
        }
    }
}




// END OF FRONTEND


// REQUEST

let usr = localStorage.getItem('user')
let sess = localStorage.getItem('session')

function isJsonObject(strData) {
    try {
        JSON.parse(strData);
    } catch (e) {
        return false;
    }
    return true;
}

function delete_account() {
    let target_user = document.getElementById("target_user").value
	let xhr = new XMLHttpRequest();
	let form = document.getElementById("delete_account");
	xhr.open(form.method, form.action, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	let data = {
        "user": usr,
        "session": sess,
		"target_user": target_user
	};
	xhr.onload = function() {
		let response = null;
		if (xhr.status >= 200 && xhr.status < 300) {
			response = xhr.responseText;
		}
		if(isJsonObject(response) != true)
			return "Failure!"
		let response_obj = JSON.parse(response);
		if(response_obj.response_status) {
            console.log(response_obj)
		}
		return "Failure!";
	}

	xhr.send(JSON.stringify(data));
}

function create_vault() {
    let vault_name = document.getElementById("vault_name").value
    let vault_owner = document.getElementById("vault_owner").value
	let xhr = new XMLHttpRequest();
	let form = document.getElementById("create_vault");
	xhr.open(form.method, form.action, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	let data = {
        "user": usr,
        "session": sess,
		"vault_name": vault_name,
		"vault_owner": vault_owner
	};
	xhr.onload = function() {
		let response = null;
		if (xhr.status >= 200 && xhr.status < 300) {
			response = xhr.responseText;
		}
		if(isJsonObject(response) != true)
			return "Failure!"
		let response_obj = JSON.parse(response);
		if(response_obj.response_status) {
            console.log(response_obj)
		}
		return "Failure!";
	}

	xhr.send(JSON.stringify(data));
}

function delete_vault() {
    let vault_name = document.getElementById("target_vault_name").value
    let vault_owner = document.getElementById("target_vault_owner").value
	let xhr = new XMLHttpRequest();
	let form = document.getElementById("delete_vault");
	xhr.open(form.method, form.action, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	let data = {
        "user": usr,
        "session": sess,
		"vault_name": vault_name,
		"vault_owner": vault_owner
	};
	xhr.onload = function() {
		let response = null;
		if (xhr.status >= 200 && xhr.status < 300) {
			response = xhr.responseText;
		}
		if(isJsonObject(response) != true)
			return "Failure!"
		let response_obj = JSON.parse(response);
		if(response_obj.response_status) {
            console.log(response_obj)
		}
		return "Failure!";
	}

	xhr.send(JSON.stringify(data));
}

function change_permission_level() {
    let permission_level = document.getElementById("permission_level").value
    permission_level = parseInt(permission_level)
    let target_user = document.getElementById("target_usr").value
	let xhr = new XMLHttpRequest();
	let form = document.getElementById("change_permission_level");
	xhr.open(form.method, form.action, true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	let data = {
        "user": usr,
        "session": sess,
        "target_user": target_user,
        "permission_level": permission_level
	};
	xhr.onload = function() {
		let response = null;
		if (xhr.status >= 200 && xhr.status < 300) {
			response = xhr.responseText;
		}
		if(isJsonObject(response) != true)
			return "Failure!"
		let response_obj = JSON.parse(response);
		if(response_obj.response_status) {
            console.log(response_obj)
		}
		return "Failure!";
	}

	xhr.send(JSON.stringify(data));

    //dodaj try int permission level
}
