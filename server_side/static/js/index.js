let i = 0;
let txt = 'Welcome to Xena systems';
let speed = 100;
function titleWriter() {
	if (i < txt.length) {
		document.getElementById("title").innerHTML += txt.charAt(i);
		console.log(txt.charAt(i))
		i++;
		setTimeout(titleWriter, speed);
	}
}

titleWriter()