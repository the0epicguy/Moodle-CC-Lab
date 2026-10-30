# Practical: VirtualBox Installation, Multiple OS Instances, Full and Para-Virtualization

## 1. Aim

To install and configure Oracle VM VirtualBox, run multiple operating system instances on one physical computer, and study full virtualization and paravirtualization.

## 2. Requirements

- Windows host computer with Intel VT-x or AMD-V hardware virtualization support.
- Oracle VM VirtualBox.
- Ubuntu Desktop ISO (and another OS ISO if a second, different guest OS is being installed).
- Sufficient RAM and free disk space.

## 3. Theory

### Virtualization

Virtualization creates virtual versions of computing resources such as CPU, memory, storage and network interfaces. It allows multiple virtual machines (VMs) to run on one physical computer. The physical computer is the **host** and each VM is a **guest**. The virtualization software layer is called a **hypervisor** or Virtual Machine Monitor (VMM).

### Full virtualization

In full virtualization, the hypervisor provides virtual hardware to the guest operating system. The guest OS can generally run without being modified specifically for the hypervisor.

```text
Applications
     |
Guest Operating System
     |
Virtual CPU, RAM, Disk and Network
     |
VirtualBox Virtualization Layer
     |
Host Operating System
     |
Physical Hardware
```

### Traditional paravirtualization

In traditional paravirtualization, the guest OS is modified or virtualization-aware. It communicates with the hypervisor using **hypercalls** for supported operations. This can reduce overhead for some operations, but requires guest OS support.

```text
Applications
     |
Virtualization-aware / modified Guest OS
     |
Hypercall Interface
     |
Hypervisor
     |
Physical Hardware
```

### Important note about the KVM setting

In VirtualBox, the VM's **System → Acceleration → Paravirtualization Interface** setting was set to **KVM** for the Ubuntu guest. This exposes a KVM-compatible paravirtualization interface to the guest. It does not convert a standard Ubuntu installation into a classical modified paravirtualized guest, such as a traditional Xen paravirtualized guest. The guest OS must recognize and use the interface.

## 4. Procedure

### Part A: Install VirtualBox

1. Download the Windows installer for Oracle VM VirtualBox from the official VirtualBox website.
2. Run the installer and follow the installation wizard.
3. Retain the required default components.
4. Allow installation of required network interfaces when prompted.
5. Complete the installation and open VirtualBox Manager.

### Part B: Check hardware virtualization

1. Open Windows Task Manager.
2. Select **Performance → CPU**.
3. Find the **Virtualization** entry and confirm that it is **Enabled**.
4. If disabled, enable Intel Virtualization Technology (VT-x) or AMD SVM in BIOS/UEFI, if supported.

### Part C: Download Ubuntu

1. Visit https://ubuntu.com/download/desktop.
2. Download the Ubuntu Desktop ISO.
3. Note the location of the downloaded ISO file.

### Part D: Create the Ubuntu VM

1. Open VirtualBox Manager and click **New**.
2. Enter a VM name, for example, `Ubuntu-Lab`.
3. Select the Ubuntu ISO file.
4. Confirm the operating system type and version.
5. Allocate RAM and CPUs according to the host computer's available resources. The example values discussed during setup were 4 GB RAM and 2 CPUs.
6. Create a virtual hard disk. An example size discussed was 25–30 GB with dynamically allocated storage.
7. Review the configuration and finish creating the VM.

*Note: These RAM, CPU and disk values are examples. Record the actual values used on your computer.*

### Part E: Install Ubuntu

1. Select the Ubuntu VM and click **Start**.
2. Wait for the Ubuntu installer to load.
3. Select the language and keyboard layout.
4. Follow the installer and complete the operating system installation.
5. Restart the VM when prompted.
6. If it boots into the installer again, eject the ISO from the virtual optical drive and restart.
7. Log in and confirm that the Ubuntu desktop loads.

### Part F: Configure the paravirtualization interface

1. Shut down the Ubuntu VM completely. Do not leave it in a saved state.
2. Select the VM in VirtualBox Manager and open **Settings**.
3. Select **System**.
4. Change the settings experience level to **Expert** if advanced settings are hidden.
5. Open the **Acceleration** tab.
6. Find **Paravirtualization Interface** and select **KVM** for the Ubuntu guest.
7. Keep hardware virtualization and nested paging enabled if those options are available and supported.
8. Click **OK** to save the settings.
9. Start the Ubuntu VM again.

### Part G: Verify Ubuntu

1. Open the Terminal inside Ubuntu.
2. Run these commands one at a time:

```bash
uname -a
```
Displays kernel and system information.

```bash
cat /etc/os-release
```
Displays the installed distribution and version.

```bash
free -h
```
Displays memory information available to the guest.

```bash
nproc
```
Displays the number of processing units available to the guest.

3. Observe the outputs to confirm that Ubuntu is running inside the virtual machine and can access its allocated virtual resources.

### Part H: Run multiple OS instances

1. Return to VirtualBox Manager and click **New**.
2. Select the ISO for the second virtual machine.
3. Assign suitable RAM, CPU and virtual disk resources.
4. Complete VM creation and install the second guest operating system.
5. Start both VMs and demonstrate that they run independently.
6. Explain that each VM has its own virtual hardware configuration and virtual disk, while sharing the host computer's physical resources.

*Use the actual second OS installed during your practical. If both VMs use Ubuntu, they still demonstrate multiple independent OS instances.*

## 5. Observations

Fill in the actual values observed on your computer.

| Parameter | Observation |
|---|---|
| Host operating system | Windows |
| Virtualization software | Oracle VM VirtualBox |
| First guest OS | Ubuntu |
| Second guest OS | Enter the OS actually installed |
| Paravirtualization interface | KVM |
| Guest RAM | Enter configured value |
| Guest CPUs | Enter configured value |
| Virtual disk size | Enter configured value |
| `uname -a` | Record terminal output |
| `cat /etc/os-release` | Record Ubuntu release |
| `free -h` | Record terminal output |
| `nproc` | Record terminal output |

## 6. Full virtualization vs. traditional paravirtualization

| Basis | Full virtualization | Traditional paravirtualization |
|---|---|---|
| Guest OS | Generally unmodified | Modified or virtualization-aware |
| Communication | Through virtualized hardware and hypervisor mechanisms | Uses hypercalls |
| Compatibility | Broad guest OS compatibility | Requires guest OS support |
| Overhead | May have additional virtualization overhead | Can reduce overhead for some operations |
| Example | Standard Ubuntu VM in VirtualBox | Traditional Xen paravirtualized guest |

## 7. Result

Oracle VM VirtualBox was installed and configured. An Ubuntu virtual machine was created, the guest OS was installed and verified using Linux terminal commands. The VM's Paravirtualization Interface was configured to KVM through the Expert settings. Multiple virtual machine instances were created and run independently on the same host computer.

The practical demonstrated a full-virtualization-style VM and the configuration of VirtualBox's KVM paravirtualization interface. The KVM interface setting is not the same as converting Ubuntu into a traditional modified paravirtualized guest.

## 8. Precautions

1. Ensure hardware virtualization is enabled in BIOS/UEFI.
2. Do not allocate so much RAM or CPU that the host becomes unresponsive.
3. Keep enough free disk space for virtual disks.
4. Shut down the VM before changing settings that require it to be powered off.
5. Use an ISO that matches the intended guest OS.
6. Save work inside the guest before shutting it down.
7. Do not describe the KVM interface setting as proof that Ubuntu became a traditional modified paravirtualized OS.

## 9. Conclusion

VirtualBox allows multiple isolated virtual machines to run on one physical computer. Each VM receives virtualized CPU, memory, storage and network resources. This practical covered installation and configuration of VirtualBox, creation and verification of an Ubuntu VM, configuration of the KVM paravirtualization interface, and the conceptual differences between full virtualization and traditional paravirtualization.
