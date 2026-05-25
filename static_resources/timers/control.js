async function pause(short_code) {
    // let timers = document.getElementsByClassName("timer");
    // for (let timer of timers) {
    //     let timer_id = timer.attributes.getNamedItem("data-table").value;
    //     let remaining = timer.attributes.getNamedItem("data-remaining").value;
    //     let start_time = Date.parse(timer.attributes.getNamedItem("data-start-time").value) + 1;
    //     if (timer_id === "") {
    //         timer.attributes.getNamedItem("data-remaining").value = (((start_time + (remaining * 1000)) - Date.now()) / 1000).toFixed(0);
    //     }
    //     timer.attributes.getNamedItem("data-running").value = "false";
    // }

    let response = await fetch("/api/pause/" + short_code, {
        method: "POST", headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin'
    });
    await response.text()

    await fetchTimerUpdates(short_code);
    updateTimers();
}

async function play(short_code) {
    let response = await fetch("/api/play/" + short_code, {
        method: "POST", headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin'
    });
    await response.text()
    await fetchTimerUpdates(short_code);
    updateTimers();
}

async function reset(short_code) {
    let response = await fetch("/api/reset/" + short_code, {
        method: "POST", headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin'
    });
    await response.text();
    await fetchTimerUpdates(short_code);
    updateTimers();
}
