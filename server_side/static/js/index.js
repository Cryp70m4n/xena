let arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

let body_row = document.getElementById("table_body");
let head_row = document.getElementById("table_head");
let head_cell = head_row.insertCell(0);
head_cell.innerHTML = "Page 1";

function create_table() {
	for(let r = 0; r < 5;r++) {
		let body_cell = body_row.insertCell(0);
		body_cell.innerHTML = arr[r];
	}
}


function delete_table() {
	body_row.innerHTML = "";
}

let i = 5;
let k = 1;

create_table();

function next() {
	delete_table();
	if(i >= arr.length) {
		i = 5;
		k = 1;
		return create_table();
	}
	head_cell.innerHTML = "Page"+k;
	while(i < arr.length) {
		let body_cell = body_row.insertCell(0);
		body_cell.innerHTML = arr[i];
		i++;
	}
	k++;
}