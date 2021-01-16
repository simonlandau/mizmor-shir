function showMore() {
    var moreText = document.getElementById("more");
    var btnText = document.getElementById("showbutton");
  
    if (btnText.innerHTML == "Read more...") {
      btnText.innerHTML = "Read less...";
      moreText.style.display = "inline";
    } else {
      moreText.style.display = "none";
      btnText.innerHTML = "Read more...";
    }
  }