# Contabo VPS Setup Guide

Set up a VPS on Contabo for running ACFS and coding agents.

---

## Provider Overview

**Contabo** is a German hosting provider known for exceptional value - high specs at low prices.

| Aspect | Details |
|--------|---------|
| **Recommended Tier** | Cloud VPS S or M (~$6-12/mo) |
| **Minimum Specs** | 4 vCPU, 8GB RAM, 100GB SSD |
| **Best For** | Budget-conscious users who want high specs |
| **Signup** | [contabo.com](https://contabo.com/en/vps/) |

### Pros
- Incredible value (most RAM/storage for price)
- German engineering and data protection
- Simple control panel
- No hidden fees

### Cons
- Provisioning can take 1-3 hours (not instant)
- Support is email-only
- Fewer data center locations

---

## Step 1: Create an Account

1. Go to [contabo.com](https://contabo.com)
2. Click "Cloud VPS" in the menu
3. Select a plan and click "Configure"

![Contabo Step 1: Select VPS](screenshots/contabo-step1-select-vps.png)

---

## Step 2: Choose Your VPS Plan

Contabo offers exceptional specs for the price:

| Plan | vCPU | RAM | Storage | Price |
|------|------|-----|---------|-------|
| VPS S | 4 | 8GB | 200GB | ~$6/mo |
| VPS M | 6 | 16GB | 400GB | ~$11/mo |
| VPS L | 8 | 30GB | 800GB | ~$18/mo |

**Recommended**: VPS S (plenty for ACFS)

![Contabo Step 2: Choose plan](screenshots/contabo-step2-choose-plan.png)

---

## Step 3: Select Data Center Region

Choose a location closest to you:
- **Europe**: Germany (Nuremberg, Munich), UK
- **Americas**: US East, US Central, US West
- **Asia-Pacific**: Singapore, Japan, Australia

![Contabo Step 3: Select region](screenshots/contabo-step3-select-region.png)

---

## Step 4: Choose Operating System

1. Under "Image", select **Ubuntu 24.04**
2. Leave default storage type (SSD)

![Contabo Step 4: Select Ubuntu](screenshots/contabo-step4-select-os.png)

---

## Step 5: Set Root Password

Contabo requires a root password during setup.

1. Enter a strong password (you'll change this later)
2. Save this password temporarily

![Contabo Step 5: Set password](screenshots/contabo-step5-set-password.png)

---

## Step 6: Add Your SSH Key (Optional but Recommended)

1. Scroll to "Add-ons" section
2. Find "SSH Key" option
3. Paste your public SSH key

If you don't have an SSH key yet:
```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
cat ~/.ssh/id_ed25519.pub
```

![Contabo Step 6: Add SSH key](screenshots/contabo-step6-add-ssh-key.png)

---

## Step 7: Complete the Order

1. Review your configuration
2. Accept terms of service
3. Complete payment

**Note**: Contabo provisioning takes 1-3 hours (not instant).
You'll receive an email when your VPS is ready.

![Contabo Step 7: Complete order](screenshots/contabo-step7-complete-order.png)

---

## Step 8: Find Your IP Address

When you receive the "VPS Ready" email:

1. Log into [my.contabo.com](https://my.contabo.com)
2. Go to "Your services" > "VPS"
3. Copy the **IP address**

![Contabo Step 8: Find IP](screenshots/contabo-step8-find-ip.png)

---

## Step 9: First Login

Contabo uses `root` as the default user:

```bash
ssh root@YOUR_IP_ADDRESS
```

You'll be prompted to enter the root password from Step 5.

---

## Step 10: Create Ubuntu User (Required for ACFS)

ACFS expects an `ubuntu` user. Create it:

```bash
# Create user with sudo
adduser ubuntu
usermod -aG sudo ubuntu

# Set up SSH for the new user
mkdir -p /home/ubuntu/.ssh
cp ~/.ssh/authorized_keys /home/ubuntu/.ssh/
chown -R ubuntu:ubuntu /home/ubuntu/.ssh
chmod 700 /home/ubuntu/.ssh
chmod 600 /home/ubuntu/.ssh/authorized_keys

# Enable passwordless sudo
echo "ubuntu ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/ubuntu
```

Now reconnect as ubuntu:
```bash
exit
ssh ubuntu@YOUR_IP_ADDRESS
```

---

## Contabo-Specific Notes

### Default User
Contabo uses `root` by default. You must create the `ubuntu` user manually (see Step 10).

### Provisioning Time
Unlike other providers, Contabo takes 1-3 hours to provision. Be patient.

### Firewall
No firewall is enabled by default. Consider setting up UFW:
```bash
sudo ufw allow OpenSSH
sudo ufw enable
```

### Support
- Email: support@contabo.com
- Knowledge Base: [contabo.com/support](https://contabo.com/en/support/)

---

## Next Step

Once connected as `ubuntu`, run the ACFS installer:

```bash
curl -fsSL https://raw.githubusercontent.com/Dicklesworthstone/agentic_coding_flywheel_setup/main/install.sh | bash
```

---

*Screenshots are placeholders. Replace with actual screenshots from Contabo control panel.*
