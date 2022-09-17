let i = 0;
let txt = 'Welcome to Xena systems';
let speed = 100;
function titleWriter() {
	if (i < txt.length) {
		document.getElementById("title").textContent += txt.charAt(i);
		i++;
		setTimeout(titleWriter, speed);
	}
}

titleWriter()