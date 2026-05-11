# Configs

This folder contains configuration files used by the AI inference infrastructure.

---

## ollama-override.conf

Configures Ollama to listen on all network interfaces instead of localhost only.
Required when Ollama runs on a separate VM from your AI agents.

Without this config Ollama only binds to 127.0.0.1:11434 and remote VMs cannot reach it.

Installation:

sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo cp ollama-override.conf /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart ollama

Verify it worked:

ss -tlnp | grep 11434

Should show 0.0.0.0:11434 not 127.0.0.1:11434