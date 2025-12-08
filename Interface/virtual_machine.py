from proxmoxer import ProxmoxAPI
import sys
import time  # Import time module for sleep functionality

# Proxmox API configuration
PROXMOX_HOST = "192.168.23.141"
PROXMOX_USER = "root@pam"  # Use your Proxmox username here
PROXMOX_TOKEN = "c6009196-4df1-4dfb-9e93-ed24558e6fbf"  # Your provided API token

def manage_vm(action, vm_id):
    try:
        # Connect to Proxmox using API token
        proxmox = ProxmoxAPI(PROXMOX_HOST, user=PROXMOX_USER, token_name='bilal', token_value=PROXMOX_TOKEN, verify_ssl=False)

        # Start or stop container based on action
        if action == "on":
            print(f"Starting container {vm_id}...")
            proxmox.nodes('pve').lxc(vm_id).status.start.post()
 	# Wait
            time.sleep(10)
            proxmox.nodes('pve').lxc(vm_id).status.reboot.post()  # Use the correct node name
            print(f"Container {vm_id} started successfully.")
        elif action == "off":
            print(f"Stopping container {vm_id}...")
            proxmox.nodes('pve').lxc(vm_id).status.stop.post()
            print(f"Container {vm_id} stopped successfully.")
        else:
            print("Invalid action. Use 'on' or 'off'.")
    except Exception as e:
        print(f"Error managing container {vm_id}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python virtual_machine.py <action> <vm_id>")
    else:
        action, vm_id = sys.argv[1], sys.argv[2]
        print(f"Action: {action}, VMID: {vm_id}")
        manage_vm(action, vm_id)
