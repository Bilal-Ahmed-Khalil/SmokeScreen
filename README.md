
## 🔐 SMOKE SCREEN – Cybersecurity Deception Platform

**SMOKE SCREEN** is a final year project developed by students of Riphah International University, Faculty of Computing. It is a dynamic cybersecurity deception platform designed to protect critical infrastructure by deploying realistic decoys and honeypots to detect, engage, and mislead attackers.

### 🎯 Project Goals
- Strengthen defenses against insider and outsider threats.
- Deploy believable decoys to mimic real organizational assets.
- Generate actionable threat intelligence through attacker interaction.
- Support SCADA, ICS, finance, and healthcare environments.
- Integrate with SIEM systems and endpoint protection tools.

### 🧩 Key Modules
- **ESXi Virtualization**: Hosts Docker containers and high-interaction machines.
- **OVS Rules Engine**: Allocates decoys based on network traffic.
- **Docker Decoys**: Includes Cowrie, Conpot, Snare Tanner, and custom payment gateways.
- **Controller Module**: Algorithm-driven honeypot deployment and switching.
- **Log & Search Module**: Captures attacker behavior for adaptive rule updates.

### 🛠️ Technologies Used
- **Languages**: Python, Java, C#, C++, JavaScript, HTML, CSS  
- **Tools**: Docker, VMware ESXi, Open vSwitch, Git, GitHub  
- **IDE**: Visual Studio Code, PyCharm  
- **Platforms**: Windows & Linux

### 📊 Evaluation Strategy
- Simulated attack scenarios for interaction testing.
- Benchmarking against existing deception systems.
- Visualization dashboards and SIEM integration.

### 📁 Repository Structure
```
/docs         → Project documentation and references  
/src          → Source code for modules and decoys  
/config       → Configuration files for OVS and Docker  
/logs         → Sample attacker interaction logs  
/visuals      → Architecture diagrams and dashboards  
```

