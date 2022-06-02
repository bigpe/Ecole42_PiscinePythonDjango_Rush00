  window.addEventListener("keydown", (event) => {
	if (event.code === "ArrowUp") {
	  return document.getElementById("control-up").click();
	}
	if (event.code === "ArrowDown") {
	  return document.getElementById("control-down").click();
	}
	if (event.code === "ArrowLeft") {
	  return document.getElementById("control-left").click();
	}
	if (event.code === "ArrowRight") {
	  return document.getElementById("control-right").click();
	}
	if (event.code === "KeyA") {
	  return document.getElementById("control-a").click();
	}
	if (event.code === "KeyB") {
	  return document.getElementById("control-b").click();
	}
	if (event.code === "KeyE") {
	  return document.getElementById("control-select").click();
	}
	if (event.code === "KeyS") {
	  return document.getElementById("control-start").click();
	}
  });
