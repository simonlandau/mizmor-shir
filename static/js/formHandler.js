document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    let midiUrl = null;
    let selTorah = null;
    let numChap = null;

    form.onsubmit = function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        selTorah = formData.get('sel-torah');
        numChap = formData.get('num-chap');
        fetch("/generate", {
            method: "POST",
            body: formData
        }).then(response => response.blob())
          .then(blob => {
            midiUrl = URL.createObjectURL(blob);
            document.getElementById('player-controls').style.display = 'block';
            document.querySelector('midi-player').src = midiUrl;
            const openTextButton = document.querySelector('.opentext');
            openTextButton.setAttribute('onClick', `window.open('https://sefaria.org/${selTorah}.${numChap.toString()}', '_blank')`);
            openTextButton.textContent = `View ${selTorah} ${numChap.toString()} on Sefaria`;
        });
    };
});