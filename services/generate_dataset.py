"""
Dataset generator for ScholarMatch.
Creates 200+ realistic Ontario scholarship records using real provider names,
real programs, and realistic eligibility criteria.
"""

import random
import csv
import json
import os
from datetime import date, timedelta


#
# Real Ontario scholarship providers and programs
# 

UNIVERSITY_PROVIDERS = [
    "University of Toronto", "University of Waterloo", "McMaster University",
    "Western University", "Queen's University", "University of Ottawa",
    "University of Guelph", "Wilfrid Laurier University", "York University",
    "Ryerson University (TMU)", "Carleton University", "University of Windsor",
    "Brock University", "Trent University", "Lakehead University",
    "Ontario Tech University", "Nipissing University", "Algoma University",
    "Laurentian University", "OCAD University"
]

CORPORATE_PROVIDERS = [
    "TD Bank", "RBC Royal Bank", "BMO Financial Group", "Scotiabank",
    "CIBC", "Deloitte Canada", "KPMG Canada", "PwC Canada",
    "Shopify", "BlackBerry QNX", "OpenText", "Manulife",
    "Sun Life Financial", "Great-West Lifeco", "Magna International",
    "Bombardier", "SNC-Lavalin", "Hydro One", "Ontario Power Generation",
    "Rogers Communications", "Bell Canada", "Telus",
    "Loblaw Companies", "Canadian Tire Corporation", "Tim Hortons Foundation"
]

GOVERNMENT_PROVIDERS = [
    "Ontario Student Assistance Program (OSAP)",
    "Ontario Graduate Scholarship (OGS)",
    "Ontario Ministry of Colleges and Universities",
    "Government of Canada", "Natural Sciences and Engineering Research Council (NSERC)",
    "Social Sciences and Humanities Research Council (SSHRC)",
    "Canadian Institutes of Health Research (CIHR)",
    "Ontario Trillium Foundation",
    "Ontario Ministry of Education"
]

FOUNDATION_PROVIDERS = [
    "Loran Scholars Foundation", "Schulich Foundation",
    "Pierre Elliott Trudeau Foundation", "Vanier Canada Graduate Scholarships",
    "Terry Fox Humanitarian Award", "McCall MacBain Foundation",
    "Canadian Merit Scholarship Foundation", "Horatio Alger Association of Canada",
    "Imasco Foundation", "Jack Kent Cooke Foundation (Canada)",
    "Community Foundations of Canada", "United Way Ontario",
    "Indspire (Indigenous Education)", "Canadian Women's Foundation",
    "Toronto Community Foundation", "Brampton Community Foundation"
]

# Realistic scholarship name templates
NAME_TEMPLATES = {
    "university": [
        "{provider} Entrance Scholarship",
        "{provider} President's Scholarship",
        "{provider} Dean's List Award",
        "{provider} Faculty of {field} Scholarship",
        "{provider} International Student Award",
        "{provider} Graduate Research Fellowship",
        "{provider} Community Leadership Award",
        "{provider} Athletic Excellence Scholarship",
        "{provider} Diversity & Inclusion Award",
        "{provider} STEM Innovation Scholarship",
        "{provider} First-Generation Student Bursary",
        "{provider} Mature Student Award",
    ],
    "corporate": [
        "{provider} Future Leaders Scholarship",
        "{provider} Women in STEM Award",
        "{provider} Community Impact Scholarship",
        "{provider} Innovation Award",
        "{provider} Co-op Excellence Scholarship",
        "{provider} Diversity Scholarship",
        "{provider} Technology Scholarship",
        "{provider} Next Generation Award",
    ],
    "government": [
        "{provider} Ontario Grant",
        "{provider} Research Award",
        "{provider} Graduate Fellowship",
        "{provider} Undergraduate Research Award",
        "{provider} Access Bursary",
    ],
    "foundation": [
        "{provider} Award",
        "{provider} Scholarship",
        "{provider} Fellowship",
        "{provider} Bursary",
        "{provider} Leadership Award",
    ]
}

FIELDS_OF_STUDY = [
    "Computer Science", "Engineering", "Business", "Health Sciences",
    "Arts", "Social Sciences", "Education", "Law", "Mathematics",
    "Environmental Science", "Nursing", "Kinesiology", "Biology",
    "Chemistry", "Physics", "Psychology", "Economics", "Political Science",
    "Communications", "Architecture"
]

DEPARTMENTS = [
    "Faculty of Science", "Faculty of Engineering", "Faculty of Arts",
    "Faculty of Health Sciences", "School of Business", "Faculty of Education",
    "Faculty of Law", "Faculty of Mathematics", "Faculty of Environment",
    "School of Computer Science"
]

DESCRIPTIONS = [
    "Awarded to students demonstrating academic excellence and community involvement.",
    "For Ontario students pursuing post-secondary education with a strong academic record.",
    "Recognizes outstanding achievement in {field} and commitment to the discipline.",
    "Supports students from underrepresented communities pursuing higher education.",
    "For students who have demonstrated leadership through extracurricular activities.",
    "Awarded based on financial need and academic merit to Ontario residents.",
    "Encourages innovation and research in {field} among undergraduate students.",
    "Provides financial assistance to first-generation post-secondary students in Ontario.",
    "Supports graduate students conducting research that benefits Ontario communities.",
    "For students enrolled in accredited Ontario institutions with a minimum GPA requirement.",
    "Recognizes academic achievement and potential for future contributions to {field}.",
    "Assists Ontario students balancing academic and work responsibilities.",
    "Supports students transferring between Ontario colleges and universities.",
    "For students with demonstrated financial need pursuing studies in {field}.",
    "Celebrates diversity and inclusion in Ontario post-secondary education.",
]


def _random_deadline():
    """Generate a random future deadline between 1 and 18 months from now."""
    days_ahead = random.randint(30, 540)
    return (date.today() + timedelta(days=days_ahead)).isoformat()


def _random_amount_range():
    """Generate realistic scholarship amount ranges."""
    tiers = [
        (500, 1000),      # small bursaries
        (1000, 2500),     # standard bursaries
        (2000, 5000),     # mid-range scholarships
        (5000, 10000),    # large scholarships
        (10000, 25000),   # major awards
        (25000, 50000),   # prestigious awards
        (50000, 100000),  # elite scholarships (Loran, Schulich, etc.)
    ]
    weights = [15, 25, 25, 15, 10, 6, 4]
    tier = random.choices(tiers, weights=weights, k=1)[0]
    
    amount_min = random.randint(tier[0], (tier[0] + tier[1]) // 2)
    amount_max = random.randint(amount_min, tier[1])
    
    # Round to nice numbers
    amount_min = round(amount_min / 250) * 250
    amount_max = round(amount_max / 250) * 250
    if amount_min <= 0:
        amount_min = 250
    if amount_max < amount_min:
        amount_max = amount_min
    
    return amount_min, amount_max


def _random_eligibility():
    """Generate realistic eligibility criteria."""
    eligibility = {
        "education_level": random.choice([
            ["university"],
            ["university"],
            ["college"],
            ["university", "college"],
            ["university", "college"],
        ]),
        "provinces": random.choice([
            ["ontario"],
            ["ontario"],
            ["ontario"],  # heavily weighted toward Ontario
            ["ontario", "quebec"],
            ["ontario", "british columbia", "alberta"],
        ]),
    }
    
    # ~60% have a GPA requirement
    if random.random() < 0.6:
        eligibility["min_gpa"] = round(random.choice([2.5, 2.7, 3.0, 3.2, 3.5, 3.7, 3.8, 3.9]), 1)
    
    # ~15% require first-gen status
    if random.random() < 0.15:
        eligibility["first_gen"] = True
    
    # ~10% target minority students
    if random.random() < 0.10:
        eligibility["minority"] = True
    
    return eligibility


def _random_citizenship():
    """Generate citizenship requirement distribution."""
    return random.choices(
        ["any", "canadian", "canadian_or_pr"],
        weights=[50, 30, 20],
        k=1
    )[0]


def _random_fields():
    """Generate a list of eligible fields of study (or empty for open scholarships)."""
    # ~30% are open to all fields
    if random.random() < 0.3:
        return []
    
    num_fields = random.randint(1, 5)
    return random.sample(FIELDS_OF_STUDY, num_fields)


def _generate_url(provider, name):
    """Generate a plausible URL for the scholarship."""
    slug = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
    slug = slug.replace("&", "and").replace("'", "").replace(",", "")
    # Truncate long slugs
    slug = slug[:60]
    domain = provider.lower().split()[0].replace("(", "").replace(")", "")
    return f"https://www.{domain}.ca/scholarships/{slug}"


def generate_scholarships(count=220, seed=42):
    """
    Generate a list of realistic Ontario scholarship records.
    
    Args:
        count: Number of scholarships to generate (default 220 to exceed 200 after cleaning)
        seed: Random seed for reproducibility
    
    Returns:
        List of scholarship dictionaries
    """
    random.seed(seed)
    scholarships = []
    
    # Build provider pool with category tags
    provider_pool = []
    for p in UNIVERSITY_PROVIDERS:
        provider_pool.append((p, "university"))
    for p in CORPORATE_PROVIDERS:
        provider_pool.append((p, "corporate"))
    for p in GOVERNMENT_PROVIDERS:
        provider_pool.append((p, "government"))
    for p in FOUNDATION_PROVIDERS:
        provider_pool.append((p, "foundation"))
    
    used_names = set()
    
    for i in range(count):
        provider, category = random.choice(provider_pool)
        templates = NAME_TEMPLATES[category]
        fields = _random_fields()
        
        # Pick a field for the name template
        field_name = random.choice(fields) if fields else random.choice(FIELDS_OF_STUDY)
        
        # Generate unique name
        attempts = 0
        while attempts < 20:
            template = random.choice(templates)
            name = template.format(provider=provider, field=field_name)
            if name not in used_names:
                used_names.add(name)
                break
            attempts += 1
        else:
            # Append a number if we can't find a unique name
            name = f"{name} #{i}"
            used_names.add(name)
        
        amount_min, amount_max = _random_amount_range()
        eligibility = _random_eligibility()
        
        description_template = random.choice(DESCRIPTIONS)
        description = description_template.format(field=field_name)
        
        scholarship = {
            "id": i + 1,
            "name": name,
            "provider": provider,
            "amount_min": amount_min,
            "amount_max": amount_max,
            "deadline": _random_deadline(),
            "eligibility": json.dumps(eligibility),  # Store as JSON string for CSV
            "field_of_studys": json.dumps(fields),    # Store as JSON string for CSV
            "url": _generate_url(provider, name),
            "description": description,
            "citizenship_requirement": _random_citizenship()
        }
        scholarships.append(scholarship)
    
    # ──────────────────────────────────────────────────────────────
    # Intentionally inject dirty data for the cleaning pipeline
    # ──────────────────────────────────────────────────────────────
    
    # 1. Inject ~10 rows with missing values
    for _ in range(10):
        idx = random.randint(0, len(scholarships) - 1)
        field_to_null = random.choice(["name", "provider", "amount_max", "deadline"])
        scholarships[idx][field_to_null] = ""
    
    # 2. Inject ~5 rows with type mismatches (strings where numbers should be)
    for _ in range(5):
        idx = random.randint(0, len(scholarships) - 1)
        scholarships[idx]["amount_min"] = "TBD"
        scholarships[idx]["amount_max"] = "varies"
    
    # 3. Inject ~8 exact duplicate rows
    for _ in range(8):
        idx = random.randint(0, len(scholarships) - 1)
        scholarships.append(scholarships[idx].copy())
    
    # 4. Inject ~3 rows with swapped min/max
    for _ in range(3):
        idx = random.randint(0, len(scholarships) - 1)
        if isinstance(scholarships[idx]["amount_min"], (int, float)) and isinstance(scholarships[idx]["amount_max"], (int, float)):
            scholarships[idx]["amount_min"], scholarships[idx]["amount_max"] = (
                scholarships[idx]["amount_max"], scholarships[idx]["amount_min"]
            )
    
    return scholarships


def save_dataset(scholarships, filepath):
    """Save scholarship list to CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    fieldnames = [
        "id", "name", "provider", "amount_min", "amount_max",
        "deadline", "eligibility", "field_of_studys", "url",
        "description", "citizenship_requirement"
    ]
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scholarships)
    
    print(f"\n   [DATASET] Generated {len(scholarships)} scholarship records")
    print(f"   [DATASET] Saved to: {filepath}")
    print(f"   [DATASET] Includes intentional dirty data for cleaning pipeline demo")


if __name__ == "__main__":
    data = generate_scholarships()
    save_dataset(data, os.path.join("data", "raw_scholarships.csv"))
