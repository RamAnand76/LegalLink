"""
Sample legal document templates for LegalLink.
Run this script to populate the database with starter templates.
"""
import sys
sys.path.append(".")

from app.db.session import SessionLocal
from app.crud.crud_document import document_template

SAMPLE_TEMPLATES = [
    {
        "name": "Consumer Complaint",
        "description": "Complaint for consumer protection issues - defective products, services, etc.",
        "category": "complaint",
        "required_fields": [
            "complainant_name",
            "complainant_address",
            "respondent_name",
            "respondent_address",
            "product_service",
            "purchase_date",
            "complaint_reason",
            "relief_sought"
        ],
        "field_descriptions": [
            {"field_name": "complainant_name", "description": "Full name of the complainant", "example": "Raj Kumar Singh"},
            {"field_name": "complainant_address", "description": "Complete address of the complainant", "example": "123, MG Road, Delhi"},
            {"field_name": "respondent_name", "description": "Name of the company/seller", "example": "XYZ Electronics Pvt. Ltd."},
            {"field_name": "respondent_address", "description": "Address of the company/seller", "example": "456, Industrial Area, Mumbai"},
            {"field_name": "product_service", "description": "Product or service purchased", "example": "Samsung LED TV Model ABC123"},
            {"field_name": "purchase_date", "description": "Date of purchase", "example": "15/06/2025"},
            {"field_name": "complaint_reason", "description": "Reason for complaint", "example": "Defective product, not working after 2 days"},
            {"field_name": "relief_sought", "description": "What relief is being sought", "example": "Full refund of Rs. 50,000"}
        ],
        "template_content": """BEFORE THE DISTRICT CONSUMER DISPUTES REDRESSAL FORUM
{{district_name}}

Consumer Complaint No. _________ of 20____

IN THE MATTER OF:

{{complainant_name}}
{{complainant_address}}
                                                                    ... COMPLAINANT

VERSUS

{{respondent_name}}
{{respondent_address}}
                                                                    ... OPPOSITE PARTY

COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019

RESPECTFULLY SHOWETH:

1. That the Complainant is a consumer within the meaning of Section 2(7) of the Consumer Protection Act, 2019.

2. That the Opposite Party is engaged in the business of selling/providing {{product_service}}.

3. That on {{purchase_date}}, the Complainant purchased/availed {{product_service}} from the Opposite Party for valuable consideration.

4. That the Complainant has a valid cause of action against the Opposite Party for the following reasons:
   {{complaint_reason}}

5. That despite repeated requests and communications to the Opposite Party, no satisfactory resolution has been provided.

6. That the Complainant has suffered loss and inconvenience due to the deficiency in service/defect in goods provided by the Opposite Party.

PRAYER:

In view of the above facts and circumstances, this Hon'ble Forum may be pleased to:

a) {{relief_sought}}
b) Award compensation for mental agony and harassment suffered by the Complainant
c) Award costs of litigation
d) Pass any other order as this Hon'ble Forum may deem fit and proper

Place: {{place}}
Date: {{current_date}}

                                                    ___________________
                                                    ({{complainant_name}})
                                                    COMPLAINANT

VERIFICATION

I, {{complainant_name}}, the Complainant above named, do hereby verify that the contents of paragraphs 1 to 6 of this complaint are true and correct to my knowledge and belief.

Verified at {{place}} on this {{current_date}}.

                                                    ___________________
                                                    COMPLAINANT
"""
    },
    {
        "name": "Writ Petition - Article 226",
        "description": "Writ Petition under Article 226 of the Constitution for High Court",
        "category": "petition",
        "required_fields": [
            "petitioner_name",
            "petitioner_address",
            "respondent_name",
            "respondent_designation",
            "violation_details",
            "relief_sought"
        ],
        "field_descriptions": [
            {"field_name": "petitioner_name", "description": "Full name of the petitioner"},
            {"field_name": "petitioner_address", "description": "Complete address of the petitioner"},
            {"field_name": "respondent_name", "description": "Name of the respondent authority"},
            {"field_name": "respondent_designation", "description": "Designation of the respondent"},
            {"field_name": "violation_details", "description": "Details of the rights violated"},
            {"field_name": "relief_sought", "description": "What relief is being sought"}
        ],
        "template_content": """IN THE HIGH COURT OF {{state_name}}
AT {{city_name}}

WRIT PETITION (CIVIL) NO. _______ OF 20____

IN THE MATTER OF:

{{petitioner_name}}
S/o / D/o / W/o ____________________
Aged about ____ years
R/o {{petitioner_address}}
                                                                    ... PETITIONER

VERSUS

1. {{respondent_name}}
   {{respondent_designation}}
                                                                    ... RESPONDENT(S)

WRIT PETITION UNDER ARTICLE 226 OF THE CONSTITUTION OF INDIA

TO,
THE HON'BLE CHIEF JUSTICE AND HIS COMPANION JUDGES OF THE HIGH COURT OF {{state_name}}

THE HUMBLE PETITION OF THE PETITIONER ABOVE-NAMED

MOST RESPECTFULLY SHOWETH:

1. FACTS OF THE CASE:
   That the Petitioner is a citizen of India and is entitled to the protection of fundamental rights guaranteed under the Constitution of India.

2. CAUSE OF ACTION:
   {{violation_details}}

3. LIMITATION:
   This petition is being filed within the period of limitation as the cause of action arose on or about _________.

4. There is no other equally efficacious alternative remedy available to the Petitioner except to approach this Hon'ble Court.

5. The Petitioner has not filed any similar petition before this Hon'ble Court or any other Court regarding the same cause of action.

PRAYER:

In view of the facts and circumstances stated above, it is most respectfully prayed that this Hon'ble Court may graciously be pleased to:

a) Issue a Writ of Mandamus/Certiorari/Prohibition/Quo Warranto/Habeas Corpus (as applicable) directing the Respondent(s) to:
   {{relief_sought}}

b) Pass such other and further order(s) as this Hon'ble Court may deem fit and proper in the facts and circumstances of the case.

AND FOR THIS ACT OF KINDNESS, THE PETITIONER AS IN DUTY BOUND SHALL EVER PRAY.

Place: {{place}}
Date: {{current_date}}

                                                    ___________________
                                                    PETITIONER

THROUGH:
___________________
ADVOCATE FOR PETITIONER
"""
    },
    {
        "name": "Legal Notice",
        "description": "General legal notice template for various disputes",
        "category": "notice",
        "required_fields": [
            "sender_name",
            "sender_address",
            "recipient_name",
            "recipient_address",
            "subject",
            "facts",
            "demand",
            "response_days"
        ],
        "field_descriptions": [
            {"field_name": "sender_name", "description": "Name of the person sending notice"},
            {"field_name": "sender_address", "description": "Address of the sender"},
            {"field_name": "recipient_name", "description": "Name of the recipient"},
            {"field_name": "recipient_address", "description": "Address of the recipient"},
            {"field_name": "subject", "description": "Subject of the legal notice"},
            {"field_name": "facts", "description": "Detailed facts of the matter"},
            {"field_name": "demand", "description": "What is being demanded"},
            {"field_name": "response_days", "description": "Days to respond", "example": "15"}
        ],
        "template_content": """LEGAL NOTICE

Date: {{current_date}}

To,
{{recipient_name}}
{{recipient_address}}

Subject: {{subject}}

UNDER INSTRUCTIONS FROM AND ON BEHALF OF MY CLIENT:

{{sender_name}}
{{sender_address}}

Dear Sir/Madam,

I, the undersigned, have been instructed by my client, {{sender_name}}, to address this Legal Notice to you as under:

1. FACTS OF THE MATTER:

{{facts}}

2. LEGAL POSITION:

That the above acts/omissions on your part are in clear violation of the legal rights of my client and constitute actionable wrong under the law.

3. DEMAND:

My client hereby demands that you:

{{demand}}

4. CONSEQUENCE OF NON-COMPLIANCE:

You are hereby called upon to comply with the above demand within {{response_days}} days from the receipt of this notice, failing which my client shall be constrained to initiate appropriate legal proceedings against you, both civil and/or criminal, at your risk, cost and consequences, which please note.

5. RESERVATION OF RIGHTS:

My client reserves the right to take any and all legal remedies available under law including but not limited to filing a civil suit for damages, specific performance, injunction, and/or criminal complaint as may be deemed appropriate.

This Notice is issued without prejudice to any other rights and remedies of my client under the law.

A copy of this notice is being retained for record and further legal proceedings if required.

Yours faithfully,

___________________
ADVOCATE
On behalf of {{sender_name}}

(Sent by Registered Post A.D. / Speed Post / Email)
"""
    },
    {
        "name": "Affidavit - General Purpose",
        "description": "General purpose affidavit template",
        "category": "affidavit",
        "required_fields": [
            "deponent_name",
            "father_name",
            "age",
            "address",
            "statement"
        ],
        "field_descriptions": [
            {"field_name": "deponent_name", "description": "Name of the person making affidavit"},
            {"field_name": "father_name", "description": "Father's name"},
            {"field_name": "age", "description": "Age of deponent"},
            {"field_name": "address", "description": "Residential address"},
            {"field_name": "statement", "description": "Statement being declared under oath"}
        ],
        "template_content": """AFFIDAVIT

I, {{deponent_name}}, S/o / D/o / W/o {{father_name}}, aged about {{age}} years, residing at {{address}}, do hereby solemnly affirm and declare as under:

1. That I am the deponent herein and am competent to swear this affidavit.

2. That I am making this affidavit of my own free will and without any coercion or undue influence.

3. {{statement}}

4. That the contents of this affidavit are true and correct to my knowledge and belief, and nothing material has been concealed therefrom.

5. That I understand that making a false statement herein may result in legal consequences including prosecution for perjury.

VERIFICATION

I, {{deponent_name}}, the Deponent above named, do hereby verify that the contents of this affidavit are true and correct to my knowledge and belief, and nothing material has been concealed therefrom.

Verified at {{place}} on this {{current_date}}.

                                                    ___________________
                                                    DEPONENT

BEFORE ME

NOTARY PUBLIC / OATH COMMISSIONER
"""
    },
    {
        "name": "RTI Application",
        "description": "Right to Information application under RTI Act, 2005",
        "category": "application",
        "required_fields": [
            "applicant_name",
            "applicant_address",
            "public_authority",
            "pio_designation",
            "information_sought"
        ],
        "field_descriptions": [
            {"field_name": "applicant_name", "description": "Name of the applicant"},
            {"field_name": "applicant_address", "description": "Address of the applicant"},
            {"field_name": "public_authority", "description": "Name of the public authority"},
            {"field_name": "pio_designation", "description": "Designation of the Public Information Officer"},
            {"field_name": "information_sought", "description": "Details of information being requested"}
        ],
        "template_content": """APPLICATION UNDER THE RIGHT TO INFORMATION ACT, 2005

To,
The Public Information Officer
{{pio_designation}}
{{public_authority}}

Subject: Application for seeking information under the Right to Information Act, 2005

Respected Sir/Madam,

I, {{applicant_name}}, resident of {{applicant_address}}, hereby request the following information under Section 6 of the Right to Information Act, 2005:

INFORMATION SOUGHT:

{{information_sought}}

I state that the information sought does not fall within the restrictions contained in Section 8 and 9 of the RTI Act, 2005.

I am a citizen of India, and I am enclosing the prescribed fee of Rs. 10/- (Rupees Ten only) by way of Indian Postal Order / Demand Draft / Court Fee Stamp / Cash (as applicable).

If the information sought is held by another public authority or is more closely connected with the functions of another public authority, I request you to transfer this application or the relevant part of it to that authority under Section 6(3) of the RTI Act, 2005.

If you are not the Public Information Officer of the concerned department, I request you to forward this application to the concerned PIO under Section 6(3) of the Act.

I request the information to be provided in:
[ ] Hardcopy
[ ] Soft copy (email)
[ ] Inspection of records

My contact details:
Name: {{applicant_name}}
Address: {{applicant_address}}
Mobile: {{mobile_number}}
Email: {{email}}

Place: {{place}}
Date: {{current_date}}

Thanking You,

Yours faithfully,

___________________
({{applicant_name}})
APPLICANT
"""
    }
]


def seed_templates():
    """Seed the database with sample templates."""
    db = SessionLocal()
    try:
        for template_data in SAMPLE_TEMPLATES:
            existing = document_template.get_by_name(db, name=template_data["name"])
            if not existing:
                document_template.create(
                    db,
                    name=template_data["name"],
                    description=template_data["description"],
                    category=template_data["category"],
                    template_content=template_data["template_content"],
                    required_fields=template_data["required_fields"],
                    field_descriptions=template_data.get("field_descriptions")
                )
                print(f"Created template: {template_data['name']}")
            else:
                print(f"Template already exists: {template_data['name']}")
        
        print("\nTemplate seeding completed!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_templates()
