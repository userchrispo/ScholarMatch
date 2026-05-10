"""
ScholarMatch — Scholarship Matching Pipeline for Ontario Students

Main entry point. Orchestrates:
1. User profile creation/loading
2. Scholarship data generation + scraping
3. Pandas data cleaning
4. NumPy scoring engine
5. Custom merge sort ranking
6. Matplotlib visualization
"""

import os
import json
from models.user import User
from services.generate_dataset import generate_scholarships, save_dataset
from services.data_loader import get_clean_dataframe, load_from_cache
from services.matcher import rank_scholarships, display_top_matches
from services.visualizer import plot_score_distribution


# ──────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw_scholarships.csv")
CLEAN_DATA_PATH = os.path.join(DATA_DIR, "clean_scholarships.csv")
PROFILES_DIR = os.path.join(DATA_DIR, "user_profiles")
CHARTS_DIR = os.path.join(DATA_DIR, "charts")


def display_menu():
    print("\n   ═══════════════════════════════════════════════════")
    print("   ╔═══════════════════════════════════════════════════╗")
    print("   ║            🎓  SCHOLARMATCH  🎓                  ║")
    print("   ║     Ontario Scholarship Matching Pipeline         ║")
    print("   ╚═══════════════════════════════════════════════════╝")
    print("   ═══════════════════════════════════════════════════")
    print("\n   [1]  Create New Profile")
    print("   [2]  Load Existing Profile")
    print("   [3]  Run Matching Pipeline (requires profile)")
    print("   [4]  EXIT")


def create_user():
    """Interactive user profile creation."""
    print("\n   ╔═══════════════════════════════════════════════════╗")
    print("   ║              CREATE YOUR PROFILE                  ║")
    print("   ╚═══════════════════════════════════════════════════╝\n")
    
    name = input("   Name: ").strip()
    email = input("   Email: ").strip()
    
    print("\n   Education Level Options: highschool, university, college")
    education_level = input("   Education Level: ").strip().lower()
    
    major = input("   Major (e.g., Computer Science): ").strip()
    
    while True:
        try:
            gpa = float(input("   GPA (0.0 - 4.0): ").strip())
            if 0.0 <= gpa <= 4.0:
                break
            print("   GPA must be between 0.0 and 4.0")
        except ValueError:
            print("   Please enter a valid number")
    
    while True:
        try:
            year = int(input("   Year of Study (1-6): ").strip())
            break
        except ValueError:
            print("   Please enter a valid number")
    
    province = input("   Province (ontario): ").strip().lower()
    if not province:
        province = "ontario"
    
    department = input("   Department (e.g., School of Computer Science): ").strip()
    
    print("\n   Citizenship Options: canadian, permanent_resident, international")
    citizenship = input("   Citizenship: ").strip().lower()
    if not citizenship:
        citizenship = "canadian"
    
    # Demographics
    print("\n   ── Demographics (answer y/n) ──")
    first_gen = input("   First-generation student? (y/n): ").strip().lower() == "y"
    minority = input("   Visible minority? (y/n): ").strip().lower() == "y"
    disabled = input("   Person with disability? (y/n): ").strip().lower() == "y"
    demographics = {
        "first_gen": first_gen,
        "minority": minority,
        "disabled": disabled
    }
    
    # Activities
    activities_input = input("\n   Activities/clubs (comma-separated): ").strip()
    activities = [a.strip() for a in activities_input.split(",")] if activities_input else []
    
    try:
        user = User(
            name=name, email=email, education_level=education_level,
            major=major, gpa=gpa, year=year, province=province,
            demographics=demographics, activities=activities,
            department=department, citizenship=citizenship
        )
    except ValueError as e:
        print(f"\n   ERROR: {e}")
        return None
    
    # Save profile
    os.makedirs(PROFILES_DIR, exist_ok=True)
    filename = name.lower().replace(" ", "_") + ".json"
    filepath = os.path.join(PROFILES_DIR, filename)
    user.save_stats(filepath)
    print(f"\n   ✓ Profile saved to: {filepath}")
    
    return user


def load_user():
    """Load an existing user profile from JSON."""
    print("\n   ╔═══════════════════════════════════════════════════╗")
    print("   ║              LOAD YOUR PROFILE                    ║")
    print("   ╚═══════════════════════════════════════════════════╝\n")
    
    # List available profiles
    os.makedirs(PROFILES_DIR, exist_ok=True)
    profiles = [f for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]
    
    if not profiles:
        print("   No saved profiles found. Please create one first.")
        return None
    
    print("   Available profiles:")
    for i, p in enumerate(profiles, 1):
        print(f"   [{i}] {p}")
    
    try:
        choice = int(input(f"\n   Select profile (1-{len(profiles)}): ").strip())
        if 1 <= choice <= len(profiles):
            filepath = os.path.join(PROFILES_DIR, profiles[choice - 1])
            user = User.load_stats(filepath)
            if user:
                print(f"\n   ✓ Loaded profile: {user.name}")
                print(f"     Major: {user.major} | GPA: {user.gpa} | Citizenship: {user.citizenship}")
            return user
        else:
            print("   Invalid selection")
            return None
    except ValueError:
        print("   Invalid input")
        return None


def ensure_dataset():
    """Generate the scholarship dataset if it doesn't exist."""
    if not os.path.exists(RAW_DATA_PATH):
        print("\n   [PIPELINE] Generating scholarship dataset...")
        scholarships = generate_scholarships(count=220)
        save_dataset(scholarships, RAW_DATA_PATH)
    else:
        print(f"\n   [PIPELINE] Raw dataset found: {RAW_DATA_PATH}")


def run_pipeline(user):
    """
    Execute the full scholarship matching pipeline:
    1. Generate/load data
    2. Clean with Pandas
    3. Score with NumPy
    4. Rank with custom merge sort
    5. Display results
    6. Show Matplotlib chart
    """
    print("\n   ╔═══════════════════════════════════════════════════╗")
    print("   ║         RUNNING MATCHING PIPELINE                 ║")
    print("   ╚═══════════════════════════════════════════════════╝")
    print(f"\n   User: {user.name} | {user.major} | GPA: {user.gpa} | {user.citizenship}")
    
    # Step 1: Ensure raw data exists
    ensure_dataset()
    
    # Step 2: Clean data with Pandas
    print("\n   [PIPELINE] Step 2: Cleaning data with Pandas...")
    df = get_clean_dataframe(RAW_DATA_PATH, CLEAN_DATA_PATH)
    
    if df is None or len(df) == 0:
        print("   ERROR: No scholarship data available after cleaning")
        return
    
    # Step 3 & 4: Score with NumPy + rank with merge sort
    print("\n   [PIPELINE] Step 3: Scoring with NumPy engine (6 weighted factors)...")
    print("   [PIPELINE] Step 4: Ranking with custom merge sort...")
    ranked_df = rank_scholarships(user, df)
    
    # Step 5: Display results
    display_top_matches(ranked_df, top_n=15)
    
    # Step 6: Matplotlib visualization
    print("\n   [PIPELINE] Step 5: Generating fit-score distribution chart...")
    os.makedirs(CHARTS_DIR, exist_ok=True)
    chart_path = os.path.join(CHARTS_DIR, f"{user.name.lower().replace(' ', '_')}_scores.png")
    plot_score_distribution(ranked_df, user, top_n=10, save_path=chart_path, show=True)
    
    print("\n   ═══════════════════════════════════════════════════")
    print("   ✓ Pipeline complete!")
    print("   ═══════════════════════════════════════════════════")


def main():
    user = None
    
    while True:
        display_menu()
        try:
            choice = int(input("\n   Select option (1-4): "))
        except ValueError:
            print("\n   ENTER ONE OF THE FOLLOWING: 1 - 2 - 3 - 4")
            continue
        
        if choice == 1:
            user = create_user()
        
        elif choice == 2:
            user = load_user()
        
        elif choice == 3:
            if user is None:
                print("\n   ⚠ No profile loaded. Please create or load a profile first.")
            else:
                run_pipeline(user)
        
        elif choice == 4:
            print("\n   Thank you for trying ScholarMatch! Hope you found some scholarships!!")
            break
        
        else:
            print("\n   ENTER ONE OF THE FOLLOWING: 1 - 2 - 3 - 4")


if __name__ == "__main__":
    main()