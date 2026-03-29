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

## Spot a Phish Logic

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

# Closing an Incident

**Report Abuse To: 🎣**

##  Abuse Reporting Contacts for Marketing & Email Platforms

> ⚠️ For a successful take down, your submission must call out the violation of the service's Terms of Use (TOU) or Acceptable Use Policy (AUP). Always attach **full email headers** when reporting. URLs verified February 2026.

---

### Report Abuse Collection: Marketing

| # | Platform | Parent | Region | Abuse Report URL | Web Form? | Headers Required? |
|---|----------|--------|--------|-----------------|-----------|-------------------|
| 1 | Mailchimp | Intuit | US / Global | [mailchimp.com/contact/abuse](https://mailchimp.com/contact/abuse/) | ✅ | ✅ Yes |
| 2 | SendGrid | Twilio | US / Global | [sendgrid.com/en-us/report-spam](https://sendgrid.com/en-us/report-spam) | ✅ | ✅ Yes |
| 3 | Mailgun | Sinch | US / Global | [mailgun.com/receiving-spam-from-mailgun](https://www.mailgun.com/receiving-spam-from-mailgun/) | ❌ | ✅ Yes |
| 4 | Constant Contact | Constant Contact, Inc. | US / Global | Email-based only:reportphishing@constantcontact.com | ⚠️ Limited | ✅ Attach email copy |
| 5 | Brevo (Sendinblue) | Brevo | EU / Global | [brevo.com/legal/antispampolicy](https://www.brevo.com/legal/antispampolicy/) | ✅ | Recommended |
| 6 | HubSpot | HubSpot, Inc. | US / Global | [policy.hubspot.com/abuse-prevention](https://policy.hubspot.com/abuse-prevention) | ✅ | ✅ Yes (full headers) |
| 7 | ActiveCampaign | ActiveCampaign, LLC | US / Global | [activecampaign.com/security/report-an-issue](https://www.activecampaign.com/security/report-an-issue) | ✅ | Recommended |
| 8 | Klaviyo | Klaviyo, Inc. | US / Global | [klaviyo.com/security](https://www.klaviyo.com/security) | ❌ | ✅ Forward full email |
| 9 | Salesforce Marketing Cloud | Salesforce, Inc. | US / Global | [salesforce.com/company/legal/abuse](https://www.salesforce.com/company/legal/abuse/) | ✅ | ✅ Yes (complete headers) |
| 10 | Marketo Engage | Adobe | US / Global | Email-based only: abuse@marketo.com | ❌ | ✅ Forward full email |
| 11 | Campaign Monitor | Marigold | AU / Global | Email-based only: abuse@campaignmonitor.com | ❌ | ✅ Yes (full headers) |
| 12 | Dotdigital | dotdigital EMEA Ltd | UK | Email-based only: abuse@dotdigital.com | ❌ | ✅ Forward suspicious email |
| 13 | SurveyMonkey | Momentive | US / Global | [help.surveymonkey.com/en/contact](https://help.surveymonkey.com/en/contact/) | ✅ | Include survey URL |
| 14 | Typeform | TYPEFORM, S.L. | EU / Global | [successteam.typeform.com/to/KjmZCq](https://successteam.typeform.com/to/KjmZCq) | ✅ | Include form URL |
| 15 | Trello | Atlassian | AU / Global | [atlassian.com/trust/report-abuse](https://www.atlassian.com/trust/report-abuse) | ✅ | Screenshots helpful |
| 16 | Hootsuite | Hootsuite Inc. | Canada / Global | [https://hootsuite.com/security/response](https://www.hootsuite.com/security) | ❌ | N/A |
| 17 | Sprout Social | Sprout Social, Inc. | US / Global | [bugcrowd.com/sproutsocial](https://bugcrowd.com/sproutsocial) | ❌ | N/A |
| 18 | AWeber | AWeber Systems, Inc. | US | [aweber.com/antispam.htm](https://www.aweber.com/antispam.htm) | ❌ | ✅ Yes |
| 19 | GetResponse | GetResponse S.A. | Poland / Global | [getresponse.com/legal/antispam](https://www.getresponse.com/legal/antispam) | ❌ | Recommended |
| 20 | Drip | Drip (Avenue 81) | US | [drip.com/contact/spam](https://www.drip.com/contact/spam) | ✅ | ✅ Yes |
| 21 | ConvertKit / Kit | Kit | US | [compliance.convertkit.com](https://compliance.convertkit.com/) | ✅ | ✅ Forward email |
| 22 | MailerLite | UAB MailerLite | Lithuania / Global | [mailerlite.com/report-abuse](https://www.mailerlite.com/report-abuse) | ✅ | Recommended |
| 23 | Moosend | Sitecore | US / Global | [moosend.com/anti-spam-policy](https://moosend.com/anti-spam-policy/) | ❌ | Not specified |
| 24 | Amazon SES | AWS | US / Global | [support.aws.amazon.com/contacts/report-abuse](https://support.aws.amazon.com/#/contacts/report-abuse) | ✅ | ✅ Yes (full headers) |
| 25 | Postmark | ActiveCampaign | US | Email-based only: abuse@postmarkapp.com | ❌ | ✅ Forward full email |

---
### Report Abuse Collection: Public Email Services
> ⚠️ **Always attach full email headers when reporting.** Forward suspicious emails **as attachments** (not inline) to preserve header integrity.
> Use "Forward as Attachment" or save as `.eml`/`.msg` and attach to a new message.
> 🗓️ URLs verified February 2026.

---

| # | Platform | Parent Company | Region | Abuse Report URL | Abuse Email | Reporting Notes |
|---|----------|---------------|--------|-----------------|-------------|-----------------|
| 1 | **Gmail** | Google / Alphabet | US / Global | [Report abuse form](https://support.google.com/mail/contact/abuse) | `abuse@gmail.com` | Use in-app **Report Phishing** (three-dot menu). Web form requires offender's address, full headers, subject, and body. |
| 2 | **Outlook / Hotmail / Live** | Microsoft | US / Global | [Report phishing guide](https://support.microsoft.com/en-us/office/how-do-i-report-phishing-or-junk-email-e8d1134d-bb16-4361-8264-7f44c853dc6b) | `phish@office365.microsoft.com` (phishing) `junk@office365.microsoft.com` (spam) | Use in-app **Report → Report phishing**. Send as attachment — not a plain forward. Admin portal: [security.microsoft.com](https://security.microsoft.com/reportsubmission) |
| 3 | **Yahoo Mail** | Yahoo Inc. | US / Global | [Report abuse](https://help.yahoo.com/kb/SLN26401.html) | `abuse@yahoo.com` | In-app: **Spam** dropdown → **Report a Phishing Scam**. Web form also available. |
| 4 | **Apple iCloud Mail** | Apple Inc. | US / Global | [Phishing guide](https://support.apple.com/en-us/102568) | `abuse@icloud.com` (iCloud abuse) `reportphishing@apple.com` (Apple impersonation) | Apple distinguishes phishing **impersonating Apple** vs. abuse **from iCloud accounts**. Forward as attachment in both cases. |
| 5 | **AOL Mail** | Yahoo Inc. | US / Global | [Report abuse on AOL](https://help.aol.com/articles/report-abuse-or-spam-on-aol) | `abuse@aol.com` | Shares Yahoo's backend. Use in-app **Spam** button. Postmaster unified with Yahoo at [senders.yahooinc.com](https://senders.yahooinc.com/) |
| 6 | **Proton Mail** | Proton AG | Switzerland | [Report abuse](https://proton.me/support/report-abuse) | `abuse@proton.me` | Web form, in-app **Report Phishing** button, or email. Encrypted reporting via Proton Mail welcomed. |
| 7 | **Tuta Mail** | Tutao GmbH | Germany / EU | [Phishing prevention guide](https://tuta.com/blog/how-to-prevent-phishing) | `abuse@tutao.de` | No web form. Forward phishing emails with full headers to `abuse@tutao.de`. Note: company domain is `@tutao.de` not `@tuta.com`. |
| 8 | **Zoho Mail** | Zoho Corporation | India / Global | [Report abuse form](https://www.zoho.com/report-abuse/) | `abuse@zoho.com` | Web form with category selection (spam, malware, phishing, etc.). |
| 9 | **GMX Mail** | United Internet AG | Germany / EU | [Postmaster phishing tool](https://postmaster.gmx.net/en/phishing) | N/A — web form only | Upload suspicious emails in **EML/MSG format** to the Postmaster phishing tool. No public `abuse@` email. |
| 10 | **Mail.com** | United Internet AG | Germany / Global | [Postmaster phishing tool](https://postmaster.mail.com/en/phishing) | N/A — web form only | Same Postmaster infrastructure as GMX. Upload EML/MSG files. Shares abuse handling with GMX and WEB.DE. |
| 11 | **Mailfence** | ContactOffice Group SA | Belgium / EU | [Abuse reporting KB](https://kb.mailfence.com/kb/where-should-i-send-abuse-reports/) | `abuse@mailfence.com` | Email only — no web form. PGP-encrypted reports accepted via `support@mailfence.com`. |
| 12 | **Posteo** | Posteo e.K. | Germany / EU | [Contact / Abuse team](https://posteo.de/en/site/contact) | `abuse@posteo.de` | S/MIME and PGP keys available for encrypted reporting. Separate `spamreport@posteo.de` for spam filter training only. |
| 13 | **Runbox** | Runbox Solutions AS | Norway / EU | [Abuse help page](https://help.runbox.com/spam-phishing-and-other-abuse-of-our-services/) | `abuse@runbox.com` | Email or use the support portal at [support.runbox.com](https://support.runbox.com). Forward phishing emails with full headers. |
| 14 | **BT Mail** | BT Group plc | UK | [Report abuse and phishing](https://www.bt.com/help/security/how-to-report-abuse-and-phishing) | `phishing@bt.com` (phishing) `abuse@bt.com` (general) | Forward phishing as **attachments** to `phishing@bt.com`. Domains: `@btinternet.com`, `@bt.com`. |
| 15 | **Sky Mail** | Sky UK / Comcast (Yahoo-powered) | UK | [Sky Yahoo abuse](https://uk.help.yahoo.com/kb/sky/SLN26401.html) | `abuse@sky.com` | Yahoo backend — use in-app **Spam** button. Domains: `@sky.com`, `@bskyb.com`. |
| 16 | **Virgin Media Mail** | Virgin Media O2 | UK | [NetReport form](https://netreport.virginmedia.com/) | `phishing@virginmediao2.com` | If forwarding is blocked by virus filters, save email as file and attach to a new message. |
| 17 | **TalkTalk Mail** | TalkTalk Telecom Group | UK | [Phishing help](https://help-centre.talktalk.co.uk/Broadband/Security/Phishing_emails_-_everything_you_need_to_know) | `phishing@talktalk.co.uk` | Domains: `@talktalk.net`, `@tiscali.co.uk`, `@lineone.net`, `@pipex.com`. |
| 18 | **EE Mail** | BT Group | UK | [BT abuse page](https://www.bt.com/help/security/how-to-report-abuse-and-phishing) | `phishing@bt.com` | EE is a BT subsidiary — all abuse reporting routes through BT. |
| 19 | **Fastmail** | Fastmail Pty Ltd | Australia / Global | [Phishing help](https://www.fastmail.help/hc/en-us/articles/360060590633-Phishing) | `abuse@fastmail.com` | In-app: **More → Report Phishing**. Security vulnerabilities: `security@fastmailteam.com`. |
| 20 | **Hushmail** | Hush Communications Corp. | Canada | [Spam & abuse help](https://help.hushmail.com/category/299-spam-phishing-abuse) | `abuse@hushmail.com` | No prominently published abuse email — use support contact form for formal reports. HIPAA-compliant. |
| 21 | **Rogers Email** | Rogers Communications | Canada | [Rogers Yahoo abuse](https://ca.help.yahoo.com/kb/rogers/SLN26401.html) | `abuse@rogers.com` | Yahoo-powered backend. Forward phishing with full headers pasted above the body. |
| 22 | **Bell Email** | BCE Inc. (Bell Canada) | Canada | [Security reporting](https://support.bell.ca/billing-and-accounts/security_and_privacy/reporting_security_issues) | `phish@bell.ca` (Bell impersonation) `abuse@bell.ca` (general) | Attach suspicious email to a **new** message — don't forward inline. Domains: `@bell.net`, `@sympatico.ca`. |
| 23 | **Shaw Email** | Rogers Communications | Canada | [Fraud alerts](https://support.shaw.ca/t5/internet-articles/recent-fraudulent-messages-and-phishing-attempts/ta-p/6435) | `internet.abuse@sjrb.ca` | Post-acquisition support increasingly routed through Rogers. Domain: `@shaw.ca`. |
| 24 | **Spark / Xtra Mail** | Spark New Zealand | New Zealand | [Report a scam](https://www.spark.co.nz/help/privacy-and-safety/scams-safety/report-a-scam/) | `reportphishing@xtra.co.nz` (phishing) `securityandabuse@spark.co.nz` (network abuse) | ⚠️ **Send a screenshot** — do not forward (it will be blocked by filters). |
---

### Report Abuse Collection: Social Media (TBC)


---

### National Cyber Reporting Authorities

| Country | Authority | Reporting Channel |
|---------|-----------|------------------|
| 🇺🇸 **United States** | FBI IC3 / APWG | [ic3.gov](https://www.ic3.gov/) · `reportphishing@apwg.org` |
| 🇬🇧 **United Kingdom** | NCSC | `report@phishing.gov.uk`|
| 🇨🇦 **Canada** | Canadian Anti-Fraud Centre | [antifraudcentre-centreantifraude.ca](https://www.antifraudcentre-centreantifraude.ca/)  |
| 🇦🇺 **Australia** | ACSC / ReportCyber | [cyber.gov.au/report](https://www.cyber.gov.au/report) · [Scamwatch](https://www.scamwatch.gov.au/) |
| 🇪🇺 **EU** | ENISA / National CERTs | [Anti-Fraud or EUROPOL](https://anti-fraud.ec.europa.eu/olaf-and-you/report-fraud_en) |
| 🇳🇿 **New Zealand** | CERT NZ / Netsafe | [cert.govt.nz](https://www.cert.govt.nz/) · [report.netsafe.org.nz](https://report.netsafe.org.nz/) |

---


# Pre-emptive Work

- Block disposable mail services
- Block junk TLDs — see [Palo Alto Unit42 research](https://unit42.paloaltonetworks.com/top-level-domains-cybercrime/)
- Tune encoded content detection rules
- Implement and enforce **DKIM / SPF / DMARC**
