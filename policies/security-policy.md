# Information Security Policy

**Document ID:** IT-POL-001  
**Version:** 4.1  
**Effective Date:** January 1, 2024  
**Owner:** IT Department / Chief Information Security Officer (CISO)  
**Last Reviewed:** November 30, 2023  

---

## 1. Purpose

This policy defines the information security standards and responsibilities for all employees, contractors, and third parties who access Acme Corporation's information systems, networks, and data. It is designed to protect the confidentiality, integrity, and availability of company information assets.

---

## 2. Scope

This policy applies to all Acme Corporation employees (full-time, part-time, temporary), contractors, vendors, and any third party with access to company systems or data, regardless of their location or the device used to access company resources.

---

## 3. Password Standards

### 3.1 Password Requirements

All passwords used to access company systems must meet the following minimum requirements:

- Minimum length of **14 characters**
- Must contain at least one uppercase letter, one lowercase letter, one number, and one special character (e.g., !, @, #, $)
- Must not contain the employee's name, username, or easily guessable information (e.g., birthdays, "password", "acme")
- Must not reuse any of the last **12 passwords**

### 3.2 Password Expiration

Passwords for standard user accounts must be changed every **90 days**. Privileged accounts (administrator-level) must be changed every **60 days**. The system will prompt users before expiration.

### 3.3 Password Manager

Employees are strongly encouraged to use the company-approved password manager (1Password) to generate and store unique, complex passwords. Sharing passwords between colleagues is strictly prohibited, even for system accounts.

### 3.4 Multi-Factor Authentication (MFA)

Multi-factor authentication is **mandatory** for:

- All company email accounts
- VPN access
- Cloud-based applications (e.g., Salesforce, AWS, GitHub)
- Remote desktop sessions
- Any system containing personally identifiable information (PII) or financial data

MFA must use an authenticator app (e.g., Microsoft Authenticator, Google Authenticator). SMS-based MFA is permitted only where authenticator apps are not supported.

---

## 4. Data Classification

All company data is classified into one of four tiers:

### 4.1 Public

Information intended for public distribution. No restrictions on sharing. Examples: marketing materials, press releases, public website content.

### 4.2 Internal

Information for use within the company only, not intended for external audiences. Examples: internal newsletters, general policies, meeting minutes. May be shared internally without restriction but must not be shared externally without approval.

### 4.3 Confidential

Sensitive business information that could cause harm if disclosed. Examples: employee personal data, salary information, customer contracts, financial forecasts, source code. Must be encrypted in transit and at rest. Access restricted to those with a business need.

### 4.4 Restricted

Highly sensitive information requiring the strictest controls. Examples: authentication credentials, encryption keys, trade secrets, merger/acquisition plans. Access limited to named, specifically authorized individuals. Must be encrypted and stored in approved secure systems only.

---

## 5. Acceptable Use of Company Systems

### 5.1 Permitted Uses

Company-owned systems and networks are provided for business purposes. Incidental personal use is permitted provided it does not:

- Interfere with work duties or productivity
- Consume excessive bandwidth or storage
- Violate any other provision of this policy or company code of conduct

### 5.2 Prohibited Activities

The following activities are strictly prohibited on company systems:

- Accessing, downloading, or distributing illegal content, including pirated software
- Visiting websites or downloading materials related to gambling, adult content, or illegal activities
- Installing unauthorized software, browser extensions, or applications
- Using company systems to conduct personal business ventures or generate personal income
- Attempting to bypass or circumvent security controls, firewalls, or access restrictions
- Sharing company credentials with any third party
- Connecting unauthorized personal storage devices (USB drives, external hard drives) to company equipment without IT approval
- Mining cryptocurrency or running non-work-related computational processes

---

## 6. Device Security

### 6.1 Laptop and Desktop Security

All company-issued computers must:

- Have full-disk encryption enabled (BitLocker for Windows, FileVault for Mac)
- Have the company-approved antivirus/endpoint protection software installed and running
- Have automatic OS and software updates enabled
- Lock automatically after **5 minutes** of inactivity
- Be kept physically secure, especially when traveling

### 6.2 Mobile Device Policy

Company data accessed on mobile devices requires:

- Enrollment in the company Mobile Device Management (MDM) program
- Screen lock with PIN or biometric authentication
- Remote wipe capability enabled
- Company email and apps installed via the approved enterprise app store

Personal devices used for company work (BYOD) are subject to the same security requirements and may be subject to remote wipe of company data if lost or if employment is terminated.

### 6.3 Lost or Stolen Devices

Any lost or stolen company device must be reported to the IT Security team within **2 hours** of discovery. Call the IT Security hotline at **x4911** (available 24/7). IT will immediately revoke access credentials and remotely wipe the device.

---

## 7. Network Security

### 7.1 VPN Usage

Employees must connect to the company VPN whenever accessing company systems from outside a company office. This includes working from home, hotels, airports, and other remote locations.

### 7.2 Public Wi-Fi

Company systems must never be accessed from public Wi-Fi (coffee shops, airports, hotels) without an active VPN connection. The IT-approved VPN client must be running before connecting to any non-company network.

### 7.3 Guest Network

Visitors to company offices may use the designated guest Wi-Fi network. Employees must not use the guest network for company work, as it does not route through company security controls.

---

## 8. Data Handling and Storage

### 8.1 Approved Storage

Company data must only be stored in approved systems:
- Company-issued laptops and desktops
- Company SharePoint/OneDrive
- Company-approved cloud platforms (AWS, Azure)
- Approved project management and collaboration tools

### 8.2 Prohibited Storage

The following storage locations are prohibited for company data:

- Personal Google Drive, Dropbox, iCloud, or similar personal cloud services
- Personal USB drives or external hard drives (unless encrypted and IT-approved)
- Personal email accounts
- Any non-approved third-party system

### 8.3 Data Retention and Disposal

- Data must be retained in accordance with the company Data Retention Schedule (FIN-POL-005)
- When data is no longer needed, it must be permanently deleted using approved methods
- Hard drives and storage media must be physically destroyed or certified-wiped before disposal; contact IT for assistance

---

## 9. Incident Reporting

### 9.1 What to Report

Employees must immediately report any of the following to the IT Security team:

- Suspected malware or ransomware infection
- Unauthorized access to company systems or data
- Phishing emails or suspicious communications (use the "Report Phishing" button in Outlook)
- Loss or theft of company devices or data
- Any other suspected security breach

### 9.2 How to Report

- **Email:** security@acmecorp.com
- **Phone:** x4911 (24/7 Security Hotline)
- **IT Ticket:** via the IT Service Desk portal

Employees who report suspected incidents in good faith will not face retaliation, even if the incident turns out to be a false alarm.

### 9.3 Mandatory Reporting Timeline

Confirmed or suspected data breaches involving personal data must be reported to the CISO within **1 hour** of discovery. The CISO will determine if regulatory reporting obligations are triggered.

---

## 10. Security Awareness Training

All employees must complete:

- **Annual security awareness training** (minimum 2 hours, via the company LMS)
- **Phishing simulation exercises** (conducted quarterly by IT Security)
- **Role-specific training** for employees handling confidential or restricted data

Failure to complete mandatory security training within the deadline may result in suspension of system access until training is completed.

---

## 11. Consequences of Violations

Security policy violations are treated seriously. Depending on the severity and intent, violations may result in:

- Mandatory remedial training
- Suspension of system access
- Formal disciplinary action
- Termination of employment
- Civil or criminal legal action

---

## 12. Contact

For security questions or to report an incident: **security@acmecorp.com** | **x4911**  
For general IT support: **it-support@acmecorp.com** | **x4100**

---

*This policy must be reviewed annually and updated to reflect evolving threats, technology changes, and regulatory requirements.*
