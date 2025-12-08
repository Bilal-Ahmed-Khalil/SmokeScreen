function toggleDecoy(level, id, action) {
    fetch("/toggle_decoy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ level: level, id: id, action: action }),
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            if (!data.error) {
                const statusElement = document.getElementById(`status-${id}`);
                if (statusElement) {
                    statusElement.innerText = action === "on" ? "active" : "deactivated";
                    statusElement.style.color = action === "on" ? "green" : "red";
                }
            }
        })
        .catch(err => {
            console.error("Error toggling decoy:", err);
            alert("An error occurred while toggling the decoy.");
        });
}

function viewDetails(level, id) {
    fetch(`/get_decoy_details/${level}/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert(`Decoy Details:\nStatus: ${data.status}\nVMID: ${data.vmid}\nIP: ${data.ip}\n DETAILS: ${data.details}`);
            }
        })
        .catch(err => {
            console.error("Error fetching decoy details:", err);
            alert("An error occurred while fetching decoy details.");
        });
}
