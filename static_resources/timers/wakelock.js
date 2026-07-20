let wakeLock = null;
let handler = false;

async function handleVisibilityChange() {
    if (wakeLock !== null && document.visibilityState === 'visible') {
        await requestWakeLock();
    }
}

async function requestWakeLock() {
    if (!('wakeLock' in navigator)) {
        return
    }

    try {
        wakeLock = await navigator.wakeLock.request('screen');
        if (!handler) {
            document.addEventListener('visibilitychange', handleVisibilityChange);
            handler = true;
        }
        console.log("wakeLock acquired")
    } catch (err) {
        console.log("Unable to acquire wakeLock")
    }
}

async function releaseWakeLock() {
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    handler = false;
    if (wakeLock !== null) {
        wakeLock.release().then(() => {
            wakeLock = null;
            console.log("wakeLock released")
        })
    }
}
