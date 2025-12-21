document.addEventListener('DOMContentLoaded', () => {
    const alarmButton = document.getElementById('alarmButton');
    const resetButton = document.getElementById('resetButton');
    const statusText = document.getElementById('statusText');
    const statusIndicator = document.getElementById('statusIndicator');
    const activityLog = document.getElementById('activityLog');
    const counterMeasuresButton = document.getElementById('counterMeasuresButton');
    const callFireBrigadeButton = document.getElementById('callFireBrigadeButton');
    const callEmergencyButton = document.getElementById('callEmergencyButton');

    function logActivity(message, isAlarmActive = false) {
        const logEntry = document.createElement('li');
        logEntry.textContent = message;
        logEntry.style.backgroundColor = isAlarmActive ? '#ff4c4c' : '#c3e6cb'; // Red if alarm, green otherwise
        activityLog.appendChild(logEntry);
    }

    alarmButton.addEventListener('click', () => {
        fetch('/activate', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                statusText.textContent = 'Active';
                statusIndicator.style.backgroundColor = '#ff4c4c';
                logActivity('Alarm activated', true);
            });
    });

    resetButton.addEventListener('click', () => {
        fetch('/reset', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                statusText.textContent = 'Inactive';
                statusIndicator.style.backgroundColor = '#28a745';
                logActivity('Alarm reset');
            });
    });

    counterMeasuresButton.addEventListener('click', () => {
        fetch('/countermeasures', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                logActivity('Countermeasures initiated');
            });
    });

    callFireBrigadeButton.addEventListener('click', () => {
        fetch('/call_fire_brigade', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                logActivity('Called Fire Brigade');
            });
    });

    callEmergencyButton.addEventListener('click', () => {
        fetch('/call_emergency', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                logActivity('Called Emergency Services');
            });
    });
});
