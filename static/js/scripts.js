/**
 * Toggles a Decoy status with visual feedback
 */
async function toggleDecoy(level, id, action) {
    // Show a small "processing" toast
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 2000,
        timerProgressBar: true
    });

    try {
        const response = await fetch("/toggle_decoy", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ level: level, id: id, action: action }),
        });
        
        const data = await response.json();

        if (data.error) {
            Swal.fire({
                icon: 'error',
                title: 'Operation Failed',
                text: data.error,
                background: '#1e293b',
                color: '#fff'
            });
        } else {
            Toast.fire({
                icon: 'success',
                title: data.message || `Decoy ${id} updated.`
            });

            // Update the UI dynamically
            const statusElement = document.getElementById(`status-${id}`);
            if (statusElement) {
                const isActive = action === "on";
                statusElement.innerHTML = `<i class="bi bi-circle-fill me-1" style="font-size: 8px;"></i> ${isActive ? "ACTIVE" : "DEACTIVATED"}`;
                // Set color to match your dashboard theme (Cyan for active, Red for off)
                statusElement.style.color = isActive ? "#00f2ff" : "#ff4d4d";
            }
        }
    } catch (err) {
        console.error("Error toggling decoy:", err);
        Swal.fire({ icon: 'error', title: 'Connection Error', text: 'Could not reach the server.' });
    }
}

/**
 * Views Decoy details in a styled modal
 */
async function viewDetails(level, id) {
    try {
        const response = await fetch(`/get_decoy_details/${level}/${id}`);
        const data = await response.json();

        if (data.error) {
            Swal.fire({ icon: 'error', title: 'Error', text: data.error });
        } else {
            // Display details in a professional "System Node" layout
            Swal.fire({
                title: `<span style="color: #00f2ff">Node Details: ${id}</span>`,
                html: `
                    <div style="text-align: left; font-family: monospace; background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155;">
                        <p><strong>STATUS:</strong> <span style="color: ${data.status === 'active' ? '#00f2ff' : '#ff4d4d'}">${data.status.toUpperCase()}</span></p>
                        <p><strong>VMID:</strong> ${data.vmid}</p>
                        <p><strong>IP_ADDR:</strong> <span style="color: #ffbd2e">${data.ip}</span></p>
                        <hr style="border-color: #334155">
                        <p><strong>LOG_DATA:</strong><br><small style="color: #94a3b8">${data.details}</small></p>
                    </div>
                `,
                background: '#1e293b',
                color: '#fff',
                confirmButtonColor: '#00f2ff',
                confirmButtonText: 'Acknowledge'
            });
        }
    } catch (err) {
        console.error("Error fetching details:", err);
        Swal.fire({ icon: 'error', title: 'Connection Error', text: 'Failed to retrieve node data.' });
    }
}
