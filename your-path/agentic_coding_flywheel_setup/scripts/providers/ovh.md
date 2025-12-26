# OVHcloud VPS Setup Guide

Set up a VPS on OVHcloud for running ACFS and coding agents.

---

## Provider Overview

**OVHcloud** is a European hosting provider with global presence and competitive pricing.

| Aspect | Details |
|--------|---------|
| **Recommended Tier** | VPS Starter or Value (~$8-20/mo) |
| **Minimum Specs** | 2 vCPU, 4GB RAM, 80GB SSD |
| **Best For** | EU-based users, cost-conscious setups |
| **Signup** | [ovhcloud.com](https://www.ovhcloud.com/en/vps/) |

### Pros
- Very competitive pricing
- European data centers (GDPR compliance)
- Good network performance
- No hidden fees

### Cons
- Control panel can be complex
- Support response can be slow
- Some features require technical knowledge

---

## Step 1: Create an Account

1. Go to [ovhcloud.com](https://www.ovhcloud.com)
2. Click "Sign up" or "Create an account"
3. Complete identity verification

![OVH Step 1: Create account](screenshots/ovh-step1-create-account.png)

---

## Step 2: Navigate to VPS Section

1. Log into the OVH Control Panel
2. Click "Bare Metal Cloud" in the top menu
3. Select "VPS" from the sidebar

![OVH Step 2: Select VPS](screenshots/ovh-step2-select-vps.png)

---

## Step 3: Choose Your VPS Plan

Select a plan with at least:
- 2 vCPU
- 4GB RAM
- 80GB SSD storage

**Recommended**: VPS Starter or VPS Value

![OVH Step 3: Choose plan](screenshots/ovh-step3-choose-plan.png)

---

## Step 4: Select Operating System

1. Choose **Ubuntu 24.04 LTS** (or latest Ubuntu)
2. Leave other options at defaults

![OVH Step 4: Select Ubuntu](screenshots/ovh-step4-select-os.png)

---

## Step 5: Add Your SSH Key

This is critical for secure access.

1. In the order form, find "SSH Key" section
2. Click "Add a key"
3. Paste your public SSH key (from `~/.ssh/id_ed25519.pub`)
4. Give it a memorable name

If you don't have an SSH key yet:
```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
cat ~/.ssh/id_ed25519.pub
```

![OVH Step 5: Add SSH key](screenshots/ovh-step5-add-ssh-key.png)

---

## Step 6: Choose Data Center Location

Select a location closest to you:
- **Europe**: Gravelines (France), Strasbourg, Warsaw
- **Americas**: Beauharnois (Canada), Hillsboro (USA)
- **Asia-Pacific**: Singapore, Sydney

![OVH Step 6: Select location](screenshots/ovh-step6-select-location.png)

---

## Step 7: Complete the Order

1. Review your configuration
2. Accept terms of service
3. Complete payment

Your VPS will be provisioned within minutes.

![OVH Step 7: Complete order](screenshots/ovh-step7-complete-order.png)

---

## Step 8: Find Your IP Address

After provisioning:

1. Go to "Bare Metal Cloud" > "VPS"
2. Click on your new VPS
3. Copy the **IPv4 address**

![OVH Step 8: Find IP](screenshots/ovh-step8-find-ip.png)

---

## Step 9: Connect via SSH

```bash
ssh ubuntu@YOUR_IP_ADDRESS
```

If you used root during setup:
```bash
ssh root@YOUR_IP_ADDRESS
```

---

## OVH-Specific Notes

### Default User
OVH VPS typically uses `ubuntu` as the default user for Ubuntu images.

### Firewall
OVH has a basic firewall in the control panel. For most setups, the default configuration works fine.

### Reboot After Updates
After running `apt upgrade`, reboot the VPS:
```bash
sudo reboot
```

### Support
- Knowledge Base: [help.ovhcloud.com](https://help.ovhcloud.com)
- Community Forum: [community.ovh.com](https://community.ovh.com)

---

## Next Step

Once connected, run the ACFS installer:

```bash
curl -fsSL https://raw.githubusercontent.com/Dicklesworthstone/agentic_coding_flywheel_setup/main/install.sh | bash
```

---

*Screenshots are placeholders. Replace with actual screenshots from OVH control panel.*
