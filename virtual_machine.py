from proxmoxer import ProxmoxAPI
import sys
import time

# --- PROXMOX API CONFIGURATION ---
# Ensure these match your PVE node settings exactly
PROXMOX_HOST = "192.168.23.141"
PROXMOX_USER = "root@pam"
TOKEN_NAME   = "bilal"
TOKEN_VALUE  = "c6009196-4df1-4dfb-9e93-ed24558e6fbf"
NODE_NAME    = "pve"

def manage_vm(action, vm_id):
    """
    Connects to Proxmox and performs lifecycle actions on LXC containers.
    Used by SmokeScreen to deploy or teardown decoys.
    """
    try:
        # Initialize the API connection
        # verify_ssl=False is used for self-signed certificates common in lab environments
        proxmox = ProxmoxAPI(
            PROXMOX_HOST, 
            user=PROXMOX_USER, 
            token_name=TOKEN_NAME, 
            token_value=TOKEN_VALUE, 
            verify_ssl=False
        )

        # Reference to the specific LXC container on the node
        container = proxmox.nodes(NODE_NAME).lxc(vm_id)

        if action == "on":
            print(f"[*] Initializing decoy deployment: Container {vm_id}...")
            container.status.start.post()
            
            # Wait for the container's network and services to initialize
            print("[*] Waiting 10 seconds for service stabilization...")
            time.sleep(10)
            
            # Rebooting is often used to ensure honeypot scripts start correctly on boot
            container.status.reboot.post()
            print(f"[+] Decoy {vm_id} is now LIVE.")

        elif action == "off":
            print(f"[*] Deactivating decoy: Container {vm_id}...")
            container.status.stop.post()
            print(f"[-] Decoy {vm_id} has been SHUT DOWN.")

        else:
            print("[!] Error: Invalid action. Use 'on' or 'off'.")

    except Exception as e:
        print(f"[!] Critical Error managing container {vm_id}: {e}")

# --- CLI ENTRY POINT ---
if __name__ == "__main__":
    # The script expects arguments from the subprocess call in app.py
    # sys.argv[1] is the action (on/off), sys.argv[2] is the VMID
    if len(sys.argv) != 3:
        print("Usage: python virtual_machine.py <action> <vm_id>")
    else:
        target_action = sys.argv[1].lower()
        target_vmid = sys.argv[2]
        
        print(f"--- SmokeScreen Proxmox Controller ---")
        print(f"Action: {target_action} | Target VMID: {target_vmid}")
        
        manage_vm(target_action, target_vmid)
