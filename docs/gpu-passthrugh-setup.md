# GPU Passthrough Setup Guide

Proxmox VFIO GPU Passthrough for AI Inference Node

Hardware used: NVIDIA GeForce GTX 1060 6GB (ZOTAC)
Host: BigWorld Proxmox Node
Guest: Ubuntu 24.04 VM (ai-inference)

---

## Prerequisites

- Proxmox VE 8.x
- CPU with IOMMU support (Intel VT-d or AMD-Vi)
- IOMMU enabled in BIOS
- GPU in its own IOMMU group (no ACS workaround needed if isolated)

---

## Part 1 - Verify IOMMU on Proxmox Host

Run on BigWorld shell:

dmesg | grep -i iommu

Look for:
DMAR: IOMMU enabled

Also check the GPU IOMMU group:

lspci -v | grep -A 10 "GTX 1060"

The GTX 1060 must be alone in its IOMMU group for clean passthrough.
If other devices share the group you will need ACS override patching.

---

## Part 2 - Get GPU Device IDs

Run:

lspci -n | grep 01:00

Output for GTX 1060:

01:00.0 0300: 10de:1c03 (rev a1)
01:00.1 0403: 10de:10f1 (rev a1)

10de:1c03 is the GPU video device
10de:10f1 is the GPU HDMI audio device

Both must be bound to VFIO together.

---

## Part 3 - Configure VFIO on Host

Add VFIO kernel modules:

echo "vfio" >> /etc/modules
echo "vfio_iommu_type1" >> /etc/modules
echo "vfio_pci" >> /etc/modules
echo "vfio_virqfd" >> /etc/modules

Bind GPU device IDs to VFIO:

echo "options vfio-pci ids=10de:1c03,10de:10f1" >> /etc/modprobe.d/vfio.conf

Blacklist nouveau and nvidia on host:

echo "blacklist nouveau" >> /etc/modprobe.d/blacklist.conf
echo "blacklist nvidia" >> /etc/modprobe.d/blacklist.conf
echo "options nouveau modeset=0" >> /etc/modprobe.d/blacklist.conf

Update initramfs and reboot:

update-initramfs -u
reboot

---

## Part 4 - Verify VFIO Claimed the GPU

After reboot run:

lspci -k | grep -A 3 "01:00"

Must show:

Kernel driver in use: vfio-pci

Do not proceed until this confirms vfio-pci.
If it still shows nouveau the blacklist did not apply correctly.

---

## Part 5 - Create VM in Proxmox

VM ID: 400
Name: ai-inference
Node: BigWorldpve

OS Tab
ISO: ubuntu-24.04-live-server-amd64.iso
Storage: SSD
Type: Linux
Version: 6.x - 2.6 Kernel

System Tab
Machine: q35
BIOS: OVMF (UEFI)
Add EFI Disk: YES
EFI Storage: SSD
SCSI Controller: VirtIO SCSI single
Qemu Agent: YES
TPM: NO

Disks Tab
Bus/Device: VirtIO Block
Storage: SSD
Size: 60GB
Discard: YES
IO Thread: YES

CPU Tab
Sockets: 1
Cores: 4
Type: host

Memory Tab
Memory: 8192 MB
Ballooning: YES

Network Tab
Bridge: vmbr0
Model: VirtIO
Firewall: YES

Confirm Tab
UNCHECK Start after created
Click Finish

---

## Part 6 - Add GPU to VM

In Proxmox UI:
VM 400 → Hardware → Add → PCI Device

Settings:
Type: Raw Device
Device: 0000:01:00.0
All Functions: YES
PCI-Express: YES
Primary GPU: NO
ROM-Bar: YES

---

## Part 7 - Add kvm=off (CRITICAL for Nvidia)

Run on BigWorld shell:

echo "args: -cpu 'host,kvm=off'" >> /etc/pve/qemu-server/400.conf

Verify:

cat /etc/pve/qemu-server/400.conf | grep args

Must show:

args: -cpu 'host,kvm=off'

Without this Nvidia drivers detect the hypervisor and refuse to load.
This is a known Nvidia anti-VM protection that kvm=off bypasses.

---

## Part 8 - Install Ubuntu Server

Add temporary display for install:

qm set 400 -vga std
qm start 400

Open Proxmox console and install Ubuntu Server.

During install:
- Set username: cedshomelab
- Set server name: ai-inference
- Check OpenSSH Server: YES
- Skip all snaps

After install completes remove ISO:
VM 400 → Hardware → CD/DVD Drive → Edit → Do not use any media

Switch to headless after install:

qm stop 400
qm set 400 -vga none
qm start 400

Find VM IP in UniFi controller by MAC: bc:24:11:5d:39:0c
IP assigned: 10.10.30.135

---

## Part 9 - Install Nvidia Drivers Inside VM

SSH into VM:

ssh cedshomelab@10.10.30.135

Update system:

sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git build-essential htop

Install Nvidia drivers:

sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers autoinstall

Reboot:

sudo reboot

Verify GPU is working:

nvidia-smi

Expected output:
NVIDIA GeForce GTX 1060 6GB
Driver Version: 535.288.01
CUDA Version: 12.2
Memory: 6144MiB

---

## Part 10 - Install Ollama with GPU Support

Install Ollama:

curl -fsSL https://ollama.com/install.sh | sh

Bind Ollama to all interfaces so other VMs can reach it:

sudo systemctl stop ollama
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo cp /path/to/configs/ollama-override.conf /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl start ollama
sudo systemctl enable ollama

Verify network binding:

ss -tlnp | grep 11434

Must show 0.0.0.0:11434

Pull model:

ollama pull mistral:7b

Test inference:

ollama run mistral:7b

Type hello and verify fast response then exit with /bye

---

## Verification Checklist

- IOMMU enabled in host: YES
- VFIO claiming GPU (vfio-pci shown): YES
- VM created with q35 and UEFI: YES
- GPU added as Raw Device with All Functions: YES
- kvm=off in VM args: YES
- nvidia-smi shows GTX 1060: YES
- CUDA 12.2 detected: YES
- Ollama listening on 0.0.0.0:11434: YES
- curl from remote VM returns model list: YES

---

## Troubleshooting

VM fails to start after GPU added:
Check that kvm=off is in args
Check that vfio-pci is the kernel driver in use
Try setting rombar=0 if reset errors appear

nvidia-smi not found after drivers installed:
Reboot the VM
Run sudo ubuntu-drivers autoinstall again

Ollama only reachable on localhost:
Verify override.conf is in /etc/systemd/system/ollama.service.d/
Run systemctl daemon-reload then restart ollama
Check ss -tlnp shows 0.0.0.0 not 127.0.0.1

CrewAI cannot reach Ollama from other VM:
Verify firewall is not blocking port 11434
Test with curl http://OLLAMA_IP:11434/api/tags from agent VM