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

function delete_account() {
    let user = document.getElementById("user").value
}

function create_vault() {
    let vault_name = document.getElementById("vault_name").value
    let vault_owner = document.getElementById("vault_owner").value
}

function delete_vault() {
    let vault_name = document.getElementById("vault_name").value
    let vault_owner = document.getElementById("vault_owner").value
}

function change_permission_level() {
    let permission_level = document.getElementById("permission_level").value
    let user = document.getElementById("user").value

    //dodaj try int permission level
}