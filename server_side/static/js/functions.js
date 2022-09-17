let arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

let body_row = document.getElementById("table_body");
let page_number = document.getElementById("page_number");

function create_table() {
	for(let r = 0; r < 5;r++) {
		let body_cell = body_row.insertCell(-1);
		body_cell.innerHTML = arr[r];
	}
	page_number.innerHTML = "Page " + k;
}


function delete_table() {
	body_row.innerHTML = "";
}

let i = 5;
let k = 1;

create_table();

function next() {
	delete_table();
	k++;
	let tmp = i+5;
	if(i >= arr.length) {
		i = 5;
		k = 1;
		return create_table();
	}
	page_number.innerHTML = "Page " + k;
	while(i < tmp) {
		let body_cell = body_row.insertCell(-1);
		body_cell.innerHTML = arr[i];
		i++;
	}
}