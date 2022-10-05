function accountRequests() {    
    const arModal = document.getElementById("arModal");
    const arBtn = document.getElementById("arBtn");
    const span = document.getElementsByClassName("close")[0];

    arBtn.onclick = function() {
        arModal.style.display = "block";
    }

    span.onclick = function() {
        arModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == arModal) {
            arModal.style.display = "none";
        }
    }
}

function deleteAccount() {    
    const daModal = document.getElementById("daModal");
    const daBtn = document.getElementById("daBtn");
    const span = document.getElementsByClassName("close")[1];

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
    const span = document.getElementsByClassName("close")[2];

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
    const span = document.getElementsByClassName("close")[3];

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
    const span = document.getElementsByClassName("close")[4];

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