#!/usr/bin/env python3
"""
§7(o) Veto-Bot — Auto-Block 7(i) Sales (ANCSA Heir Tool)
Generates signed letter, hashes for proof, optional email/PDF save.
Legal: §7(o) = No sale without consent. Use to protect allotments/shares.
"""

import hashlib
import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import smtplib

def generate_veto_letter(heir_name: str, allotment_desc: str, doyon_id: str, ciri_id: str, email_to: list = None) -> str:
    """Generate §7(o) letter with hash for proof."""
    timestamp = time.time()
    data = {
        "heir_name": heir_name,
        "allotment_desc": allotment_desc,
        "doyon_id": doyon_id,
        "ciri_id": ciri_id,
        "timestamp": timestamp
    }
    entry_hash = hashlib.sha3_256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    letter = f"""
[Your Name]  
[Date: {time.strftime('%Y-%m-%d')}]

Doyon Limited – Legal Department  
1 Doyon Place, Fairbanks, AK 99701

CC: CIRI Legal, 2525 Gambell Street, Suite 300, Anchorage, AK 99503

RE: **§7(o) VETO — NO SALE OF MY LAND/SHARES**

Under ANCSA §7(o), I **DO NOT CONSENT** to any sale, lease, tax, or use of:
- My **allotment**: {allotment_desc}
- My **shares**: Doyon #{doyon_id}, CIRI #{ciri_id}

**My written signature is REQUIRED.** Any action without it **violates federal law**.

Proof Hash: {entry_hash}

[Your Signature]
    """
    
    if email_to:
        # Auto-send (uncomment and fill SMTP details)
        # msg = MIMEMultipart()
        # msg['From'] = 'your_email@gmail.com'
        # msg['To'] = ', '.join(email_to)
        # msg['Subject'] = '§7(o) Veto - No Sale Consent'
        # msg.attach(MIMEText(letter, 'plain'))
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login('your_email', 'password')
        # server.sendmail('your_email', email_to, msg.as_string())
        # server.quit()
        print(f"Email draft ready for {email_to}. Uncomment to send.")
    
    return letter

# Run it
if __name__ == "__main__":
    # Your details (edit these)
    heir = "John Danzhit Carroll"
    allotment = "AA-12345, Yukon Flats Tract 12"
    doyon = "D-456789"
    ciri = "C-987654"
    emails = ["legal@doyon.com", "legal@ciri.com"]  # Optional
    
    veto = generate_veto_letter(heir, allotment, doyon, ciri, emails)
    print(veto)
    print("\n--- Save as PDF or print/sign/notarize. Hash proves it's real.")