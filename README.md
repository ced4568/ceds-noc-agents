# Ced's NOC AI Agents

A self-hosted multi-agent AI system for Network Operations Center automation, built on a Proxmox homelab with GPU-accelerated local LLM inference.

Built by Chase Dumphord (Ced) — Platform and Digital Systems Engineer

---

## Overview

This project turns a homelab into a distributed AI infrastructure platform. Instead of paying for cloud AI APIs, all inference runs locally on a GPU-accelerated VM. CrewAI orchestrates multiple specialized agents that analyze infrastructure alerts, determine root causes, and generate structured incident reports automatically.

This is a real working system built on real homelab hardware, not a demo or tutorial project.

---

## Architecture

Biggie Proxmox Node
└── VM 300: ai-agent-lab (10.10.30.147)
    ├── Ubuntu 24.04
    ├── Python 3.12
    ├── CrewAI 1.14.4
    └── NOC Analyst Crew
         ├── Agent 1: Infrastructure Analyst
         ├── Agent 2: Root Cause Analyst
         └── Agent 3: NOC Documentation Writer

BigWorld Proxmox Node
└── VM 400: ai-inference (10.10.30.135)
    ├── Ubuntu 24.04
    ├── NVIDIA GeForce GTX 1060 6GB (VFIO Passthrough)
    ├── Nvidia Driver 535.288.01
    ├── CUDA 12.2
    └── Ollama GPU accelerated
         └── mistral:7b at 40-50 tokens per second
   

---

## Hardware

Component        | Spec
-----------------|------------------------------------------
Proxmox Cluster  | 6-node cluster
AI Agent Node    | Biggie - Intel Pentium Silver J5005 8GB RAM
AI Inference Node| BigWorld - GPU VM GTX 1060 6GB
GPU              | NVIDIA GeForce GTX 1060 6GB ZOTAC
CUDA             | 12.2
K3s Cluster      | 12-node Raspberry Pi cluster
Network          | UniFi VLAN-segmented
Storage          | TrueNAS
Tunneling        | Cloudflare Tunnels + Nginx Proxy Manager

---

## Stack

Component           | Role                    | Location
--------------------|-------------------------|------------------
Proxmox VE 8.4      | Hypervisor              | BigWorld + Biggie
Ubuntu 24.04        | Guest OS                | Both VMs
VFIO                | GPU Passthrough         | BigWorld host
Nvidia Driver 535   | GPU driver              | ai-inference VM
CUDA 12.2           | GPU compute             | ai-inference VM
Ollama              | LLM inference server    | ai-inference VM
mistral:7b          | Language model          | ai-inference VM
Python 3.12         | Runtime                 | ai-agent-lab VM
CrewAI 1.14.4       | Multi-agent framework   | ai-agent-lab VM

---

## NOC Analyst Crew

The first crew is a 3-agent NOC analyst pipeline.

### Agents

Infrastructure Analyst
- Reads raw alert data
- Identifies symptoms and affected systems
- Outputs structured symptom list

Root Cause Analyst
- Takes Infrastructure Analyst findings
- Determines most likely root cause
- Assesses cluster impact
- Recommends immediate actions

NOC Documentation Writer
- Takes all findings
- Produces formatted incident report
- Follows NOC reporting standards

### Agent Handoff Flow

Alert Input
    |
    v
Infrastructure Analyst
    | symptom list
    v
Root Cause Analyst
    | root cause + recommendations
    v
NOC Documentation Writer
    |
    v
Structured Incident Report      

---

## Sample Output

NOC Incident Report

Incident Summary
Incident ID: INC-20230167-AffectedNodes
Status: Open
Impact Level: High

Affected Systems
1. K3s-Node-4 - Unreachable for 5 minutes
2. Remaining K3s Nodes - CPU spiked to 85 percent
3. Prometheus Scrape Target - Down on K3s-Node-4
4. K3s-Node-5 and K3s-Node-6 - Pod rescheduling active

Root Cause
Network connectivity failure on K3s-Node-4 causing pod rescheduling
and CPU overload on remaining nodes.

Recommended Actions
1. Run network diagnostics on K3s-Node-4
2. Scale down non-critical workloads to reduce CPU pressure
3. Monitor remaining nodes and restore K3s-Node-4 when resolved

Priority Level
HIGH - Immediate action required

---

## Quick Start

Prerequisites
- Proxmox VE 8.x
- A VM with Nvidia GPU passthrough configured
- Ollama installed and running with GPU support
- Python 3.12 or higher

Clone the repo
git clone https://github.com/ced4568/ced-noc-ai-agents.git
cd ced-noc-ai-agents

Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install crewai crewai-tools

Configure your Ollama endpoint
Edit crews/noc_crew.py and update base_url to your Ollama IP
Example: base_url="http://YOUR_OLLAMA_IP:11434"

Pull the model on your Ollama server
ollama pull mistral:7b

Run the NOC crew
source .venv/bin/activate
python crews/noc_crew.py

---

## GPU Passthrough Setup

Full step by step guide is in docs/gpu-passthrough-setup.md

Covers:
- IOMMU verification
- VFIO module configuration
- GPU device ID binding
- nouveau blacklisting
- VM creation settings
- kvm=off requirement for Nvidia
- Nvidia driver install inside VM
- Ollama network binding configuration

---

## Roadmap

- Connect agents to live Prometheus API
- Connect agents to live Grafana alerts
- Add K3s cluster monitoring agent
- Add Proxmox node health agent
- Slack and Discord alert output
- Automated runbook generation
- Web dashboard for incident reports
- Integrate with Uptime Kuma webhooks
- Add memory persistence between crew runs
- Multi-crew orchestration

---

## Related Projects

ceds-observability-stack
https://github.com/ced4568/ceds-observability-stack
Prometheus, Grafana, Node Exporter, Blackbox Exporter, Uptime Kuma

---

## About

Built as part of Ced's Home Lab. A 6-node Proxmox cluster, 12-node Raspberry Pi K3s cluster, TrueNAS storage, UniFi networking, and full observability stack.

This lab directly supports my work as a Platform and Digital Systems Engineer and serves as a portfolio of real infrastructure engineering skills.

GitHub: https://github.com/ced4568
Domain: cedshomelab.com