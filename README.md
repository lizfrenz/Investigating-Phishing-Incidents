# Investigating Phishing Incidents
Phishing Analysis &amp; Email Forensics Guide  A comprehensive resource for CSIRT and DFIR professionals investigating email-based threats. This repo covers manual header analysis (Return-Path, Received, etc.) and forensic techniques to detect novel phishing campaigns that bypass automated sandboxes and LLM-generated social engineering.
#Phishing Investigation Guide

## Preambule

Phishing is one of the top sources of compromise per the [Verizon DBIR Report](https://www.verizon.com/business/resources/T9c8/reports/2024-dbir-data-breach-investigations-report.pdf).

Email sandboxes catch **known** phishing patterns — but fail on novel attacks. LLM-powered phishing tools now produce emails indistinguishable from legitimate business communication, defeating both automated tools and trained human eyes.

**Scope:** Resources and guidance for investigating suspicious emails that may be targeting [end-user credentials](https://www.proofpoint.com/us/blog/threat-insight/new-redline-stealer-distributed-using-coronavirus-themed-email-campaign).

---

## Problem

A phishing email could come from:

- A **compromised legitimate sender**
- An **unknown sender** using public email services (Yahoo, Gmail, Outlook)
- **Disposable email services**
- A **sales/marketing platform** weaponized for social engineering

> ⚠️ Phishing may also arrive disguised as spam or a recon attack — with the payload hidden in an "unsubscribe" link.

Phishing emails may come from **innocuous domains with no abuse reports** (verdict: "Unknown" or "Benign"). These are parked domains paired with TLS [certificate registration](https://letsencrypt.org/docs/) for subdomains.

AI-powered phishing kits make these emails **harder for tools to detect** and **harder for humans to spot**.

---

## Spot a Phish

Accuracy ratings: 🟢 Accurate | 🟡 Mostly Accurate | ⚪ Partially Accurate

**1. 🟢 Disconnect between claimed sender name and actual sending domain**
- Phishing emails spoof the "From" display name while sending from a fraudulent domain.
- Example: `From: "Company Support" <security@fraudulent-domain.com>`

**2. 🟢 Disconnect between claimed organization and domain used**
- Attackers use lookalike "typosquat" domains or free email providers.
- Example: `support@companysecurity.com` instead of `support@company.com`

**3. 🟡 Multiple redirects in URLs**
- Phishing links often use URL shorteners (bit.ly, tinyurl) or chains of redirects to evade detection.
- Note: Not all phishing URLs redirect — some go directly to a fake login page.

**4. ⚪ More than one sender hostname or IP address**
- Legitimate services (Google, Microsoft) use multiple IPs for redundancy — this alone isn't a red flag.
- Look for unexpected IPs or hostname mismatches, and check **SPF/DKIM failures** for stronger evidence.

**5. 🟢 Encoded payload in the body**
- Many phishing emails use Base64-encoded payloads, obfuscated JavaScript, VBA macros, or hidden links in HTML.

**6. 🟢 Malicious attachments**
- Common malicious file types: `.zip`, `.html`, `.docm`, `.iso`, `.pdf` with embedded scripts.
- Example: A fake PDF invoice with an embedded malware dropper.

**7. ⚪ Short lifespan or expired SSL certificate**
- Burner phishing domains often last ~14 days.
- Expired certs can be a red flag, but attackers frequently use Let's Encrypt for valid SSL.
- More reliable: **mismatched or self-signed certificates**.

**8. 🟡 Disconnect between sender's organization and URL in the body**
- Attackers construct URLs like: `https://org-name.action.random-domain.com/something`
- Exception: legitimate marketing platforms and surveys may use external domains.
- Always cross-reference with **WHOIS analysis** + domain reputation analysis.

---

## Tools

### Header Analyzers

> ⚠️ When reading **raw headers**, remember they read **bottom-up** — the sender appears at the bottom; transit hops appear at the top.

- [Google Email Header Analyzer](https://toolbox.googleapps.com/apps/messageheader/)
- [MHA Header Analyzer](https://mha.azurewebsites.net/)
- [MXToolbox Header Analyzer](https://mxtoolbox.com/EmailHeaders.aspx)

### Key Header Fields Reference

| Header Field | What It Is | What to Check |
|---|---|---|
| `Return-Path:` | Where to bounce undelivered mail | Compare with "From" for mismatches; check Authentication-Results; look for character swaps; check if it points to a known marketing service |
| `Received:` | Chronological audit log of mail hops | Originating IP; X-Originating-IP vs. Received; forged/multiple Received headers; protocol used (ESMTPSA = authenticated vs. plain SMTP) |
| `From:` | Mandatory sender display field | Mismatch with displayed name; typosquatting; Punycode version of domain in raw headers; cross-reference with Return-Path |
| `Reply-To:` | Optional alternate reply address | Mismatch with From; character substitution; cross-domain redirection; may be legitimately absent |

> *Authentication results are intentionally omitted — failed authentication should be caught automatically and is not typically an IR use case.*

---

### Content Analysis & URL Scanning

- [URLScan](https://urlscan.io/)
- [Hybrid Analysis](https://hybrid-analysis.com/)

> ⚠️ Be mindful of uploading sensitive/private data to these services — scan results may be publicly visible.

### Domain Analysis

- [DNS Dumpster](https://dnsdumpster.com/)

### Certificate Analysis

- [Censys](https://platform.censys.io/search)

### Content Decoding

- [CyberChef](https://gchq.github.io/CyberChef/)
- Python Script *(TBC)*

---

# Closing an Incident *(TBC)*

**Report Abuse To:**

- Public email services (Gmail, Yahoo, Outlook)
- Mailgun
- SurveyMonkey
- Trello

---

# Pre-emptive Work *(TBC)*

- Block disposable mail services
- Block junk TLDs — see [Palo Alto Unit42 research](https://unit42.paloaltonetworks.com/top-level-domains-cybercrime/)
- Tune encoded content detection rules
- Implement and enforce **DKIM / SPF / DMARC**
