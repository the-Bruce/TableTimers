function formatTimeDelta(delta) {
    const SEC = 1000, MIN = 60 * SEC, HRS = 60 * MIN
    let diff = Math.abs(delta);
    let sign = Math.sign(delta);
    let hrs = Math.floor(diff / HRS);
    let mins = Math.floor((diff % HRS) / MIN);
    let secs = Math.floor((diff % MIN) / SEC);
    if (Math.abs(Math.floor(diff / HRS)) > 0) {
        return `${sign * hrs}:${Math.abs(mins).toLocaleString('en-US', {minimumIntegerDigits: 2})}:${Math.abs(secs).toLocaleString('en-US', {minimumIntegerDigits: 2})}`
    } else {
        return `${(sign * mins).toLocaleString('en-US', {minimumIntegerDigits: 2})}:${Math.abs(secs).toLocaleString('en-US', {minimumIntegerDigits: 2})}`
    }
}

function progcol(prog) {
    if (prog > 0.5) {
        return "green"
    } else if (prog > 0.2) {
        return "blue"
    } else if (prog > 0) {
        return "orange"
    } else {
        return "red"
    }

}

function updateTimer(timer, running, delta, duration) {
    let text = timer.getElementsByClassName("timer-text");
    text[0].textContent = formatTimeDelta(delta);
    let prog = Math.max(0, Math.min(1, delta / (duration * 1000)));
    let halo = timer.getElementsByClassName("timer-halo-front")[0];
    if (running) {
        halo.style.stroke = progcol(prog);
    } else {
        console.log(timer.attributes.getNamedItem("data-table").value)
        halo.style.stroke = "black";
    }

    halo.style.strokeDashoffset = prog === 0 ? 0 : prog - 1;
}

function updateTimers() {
    let timers = document.getElementsByClassName("timer");
    for (let timer of timers) {
        let remaining = timer.attributes.getNamedItem("data-remaining").value;
        let duration = timer.attributes.getNamedItem("data-duration").value;
        if (timer.attributes.getNamedItem("data-running").value.toLowerCase() === "false") {
            let delta = remaining * 1000;
            updateTimer(timer, false, delta, duration)
        } else {
            let start_time = Date.parse(timer.attributes.getNamedItem("data-start-time").value) + 1;
            let delta = (start_time + (remaining * 1000)) - Date.now();
            updateTimer(timer, true, delta, duration)
        }
    }
}

function quickUpdateTimers() {
    let timers = document.getElementsByClassName("timer");
    for (let timer of timers) {
        if (timer.attributes.getNamedItem("data-running").value.toLowerCase() === "false") {
        } else {
            let remaining = timer.attributes.getNamedItem("data-remaining").value;
            let duration = timer.attributes.getNamedItem("data-duration").value;
            let start_time = Date.parse(timer.attributes.getNamedItem("data-start-time").value) + 1;
            let delta = (start_time + (remaining * 1000)) - Date.now();
            updateTimer(timer, true, delta, duration)
        }
    }
}

function cloneTimer(timer_id) {
    console.log(timer_id);
    let template = document.getElementById("timerTemplate");
    let timerProto = template.content;
    let intId = parseInt(timer_id);
    let timer = document.importNode(timerProto, true);
    let box = document.getElementById("tableTimers");
    let insertedTimer = null;
    for (let t of document.getElementsByClassName("timer")) {
        let val = parseInt(t.attributes.getNamedItem("data-table").value);
        if (val > intId) {
            insertedTimer = box.insertBefore(timer.firstElementChild, t.parentNode.parentNode);
            break;
        }
    }
    if (insertedTimer === null) {
        insertedTimer = box.insertBefore(timer.firstElementChild, null);
    }
    let header = insertedTimer.getElementsByClassName("card-header")[0];
    header.innerText = "Table " + timer_id;
    let timerInner = insertedTimer.getElementsByClassName("timer")[0];
    timerInner.attributes.getNamedItem("data-table").value = timer_id;
    return timerInner;
}

async function fetchTimerUpdates(short_code, control = false) {
    let url = new URL(document.URL);
    let params = new URLSearchParams(url.search);
    let enabled_tables = params.getAll("selectedTables");
    console.log(enabled_tables)
    let timer_data = await fetch("/api/session_state/" + short_code);
    if (timer_data.status !== 200) {
        return
    }
    let timer_json = JSON.parse(await timer_data.text());

    let title = document.getElementById("session-title");
    if (title) {
        title.textContent = timer_json["title"]
    }
    let round = document.getElementById("session-round");
    if (round) {
        round.textContent = timer_json["round"]
    }

    let timers = document.getElementsByClassName("timer");
    let existing = []
    let forceUpdate = false;
    let pendingDeletions = [];
    if (document.tabletimers.control) {
        if (Object.keys(timer_json["tables"]).length !== document.tabletimers.expected_extensions) {
            document.location.reload();
        }
    }
    for (let timer of timers) {
        let timer_id = timer.attributes.getNamedItem("data-table").value;
        if (timer_id === "") {
            timer.attributes.getNamedItem("data-remaining").value = timer_json["remaining_duration"];
        } else if (!document.tabletimers.control) {
            if (timer_id in timer_json["tables"] && (enabled_tables.length === 0 || enabled_tables.includes(timer_id))) {
                timer.attributes.getNamedItem("data-remaining").value = timer_json["tables"][timer_id]["remaining_duration"];
                existing.push(timer_id);
            } else {
                pendingDeletions.push(timer.parentElement.parentElement);
                continue
            }
        }
        timer.attributes.getNamedItem("data-running").value = timer_json["running"];
        timer.attributes.getNamedItem("data-duration").value = timer_json["duration"];
        timer.attributes.getNamedItem("data-start-time").value = timer_json["start_time"];
    }
    if (!document.tabletimers.control) {
        for (let del of pendingDeletions) {
            del.remove();
        }
        for (let timer_id in timer_json["tables"]) {
            if (!(existing.includes(timer_id)) && (enabled_tables.length === 0 || enabled_tables.includes(timer_id))) {
                let timer = cloneTimer(timer_id);
                timer.attributes.getNamedItem("data-remaining").value = timer_json["tables"][timer_id]["remaining_duration"];
                timer.attributes.getNamedItem("data-running").value = timer_json["running"];
                timer.attributes.getNamedItem("data-duration").value = timer_json["duration"];
                timer.attributes.getNamedItem("data-start-time").value = timer_json["start_time"];
                forceUpdate = true;
            }
        }
    }
    if (!timer_json["running"] || forceUpdate) {
        updateTimers()
    }
}
