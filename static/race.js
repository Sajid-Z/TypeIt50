const wordStreamE1 = document.querySelector("#word-stream");
const inputE1 = document.querySelector("#race-input");
const timerE1 = document.querySelector("#timer");

let wordStream = [];
let targetText = "";
let typedText = "";
let selectedMode = 30;
let startTime = null;
let timerInterval = null;
let correctChars = 0;
let raceState = "waiting"; // Possible states: "waiting", "running", "finished"

async function loadWords(){
    const res = await fetch("/api/words?count=100");
    const data = await res.json()
    wordStream = data.words;
    targetText = wordStream.join(" ");
    renderStream();
}

function renderStream() {
    let html = "";
    let wordStart = 0;

    while (wordStart < targetText.length) {
        let wordEnd = targetText.indexOf(" ", wordStart);

        if (wordEnd === -1) {
            wordEnd = targetText.length;
        }

        html += `<span class="word">`;

        for (let i = wordStart; i < wordEnd; i++) {
            const char = targetText[i];
            let cls = "untyped";

            if (i < typedText.length) {
                cls = typedText[i] === char ? "correct" : "incorrect";
            } else if (i === typedText.length) {
                cls = "current";
            }

            html += `<span class="${cls}">${char}</span>`;
        }

        html += `</span>`;

        if (wordEnd < targetText.length) {
            html += " ";
        }

        wordStart = wordEnd + 1;
    }

    wordStreamE1.innerHTML = html;

    const currentChar = wordStreamE1.querySelector(".current");
    const currentWord = currentChar?.closest(".word");

    if (currentWord) {
        currentWord.scrollIntoView({
            behavior: "auto",
            block: "center",
            inline: "nearest"
        });
    }
}

inputE1.addEventListener("input", (e) => {
    if (raceState === "waiting"){
        raceState = "running";
        startTime = Date.now();
        startTimer();
    }

    if (raceState === "finished"){
        inputE1.value = typedText;
        return;
    }

    typedText = inputE1.value;

    correctChars = 0;
    for(let i = 0; i<typedText.length; i++){
        if(typedText[i] === targetText[i]){
            correctChars++;
        }
    }

    renderStream();
    if(typedText.length >= targetText.length){
        finishRace();
    }
});

function startTimer(){
    let remaining = selectedMode;
    timerE1.textContent = remaining;

    timerInterval = setInterval(() => {
        remaining--;
        timerE1.textContent = remaining;

        if (remaining == 0){
            finishRace();
        }
    }, 1000);
}

async function finishRace(){
    if(raceState === "finished") return;
    raceState = "finished";
    clearInterval(timerInterval);
    inputE1.disabled = true;

    const elapsedSeconds = selectedMode;
    const minutes = elapsedSeconds / 60;
    const wpm = Math.round((correctChars/5)/minutes);
    const accuracy = typedText.length > 0 ? Math.round((correctChars/typedText.length) * 100) : 0;

    showResults(wpm, accuracy);

    try{
        const res = await fetch("/api/submit_race", {
            method: "POST",
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify({
                duration_mode: selectedMode,
                correct_chars: correctChars,
                total_chars_typed: typedText.length
            })
        });

        if(!res.ok){
            console.error("Failed to save race:", await res.text());
            return;
        }

        const data = await res.json();
        showResults(data.wpm, data.accuracy);
    }
    catch(err){
        console.error("Network error submitting data:", err);
    }
}

function showResults(wpm, accuracy){
    const resultsE1 = document.getElementById("results");
    resultsE1.style.display = "block";

    resultsE1.innerHTML = `
    <h2>Race Complete</h2>
    <p>WPM: ${wpm}</p>
    <p>Accuracy: ${accuracy}%</p>
    <button id="restart-btn">Race Again</button>`;

    document.getElementById("restart-btn").addEventListener("click", resetRace);
}

function resetRace(){
    typedText = "";
    correctChars = 0;
    raceState = "waiting";
    inputE1.disabled = false;
    inputE1.value = "";
    document.getElementById("results").style.display = "none";
    timerE1.textContent = selectedMode;
    clearInterval(timerInterval);
    loadWords();
    inputE1.focus();
}

document.querySelectorAll("#mode-select button").forEach(btn => {
    btn.addEventListener("click", () => {
        selectedMode = parseInt(btn.dataset.mode);
        resetRace();
    })
})
