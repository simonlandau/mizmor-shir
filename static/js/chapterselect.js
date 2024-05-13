document.addEventListener('DOMContentLoaded', function() {
    const selTorah = document.getElementById('sel-torah');
    const numChap = document.getElementById('num-chap');

    const bookChapters = {
        'Genesis': { max: 50, placeholder: '1 - 50' },
        'Exodus': { max: 40, placeholder: '1 - 40' },
        'Leviticus': { max: 27, placeholder: '1 - 27' },
        'Numbers': { max: 36, placeholder: '1 - 36' },
        'Deuteronomy': { max: 34, placeholder: '1 - 34' }
    };

    selTorah.addEventListener('change', function() {
        const selectedBook = selTorah.value;
        const chapterInfo = bookChapters[selectedBook];
        numChap.setAttribute('max', chapterInfo.max);
        numChap.setAttribute('placeholder', chapterInfo.placeholder);
    });
});
