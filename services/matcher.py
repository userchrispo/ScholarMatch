"""
Scoring engine and ranking system for ScholarMatch.
Uses NumPy for vectorized score computation across six weighted factors,
and a custom merge sort for ranking.
"""

import numpy as np
import pandas as pd
import json
from datetime import date


# ──────────────────────────────────────────────────────────────
# Default scoring weights
# ──────────────────────────────────────────────────────────────

DEFAULT_WEIGHTS = {
    "gpa":         0.25,
    "major":       0.20,
    "eligibility": 0.20,
    "deadline":    0.10,
    "citizenship": 0.10,
    "award_size":  0.15,
}


# ──────────────────────────────────────────────────────────────
# Individual scoring functions (vectorized with NumPy)
# ──────────────────────────────────────────────────────────────

def score_gpa(user_gpa, min_gpas):
    """
    Score based on how well user's GPA exceeds each scholarship's minimum.
    
    - If no min_gpa required (0): full score (1.0)
    - If user meets/exceeds: proportional score capped at 1.0
    - If user is below: partial score (user_gpa / min_gpa)
    
    Args:
        user_gpa: float, the user's GPA (0.0 - 4.0)
        min_gpas: numpy array of minimum GPA requirements
    
    Returns:
        numpy array of scores (0.0 - 1.0)
    """
    min_gpas = np.array(min_gpas, dtype=np.float64)
    
    # Where no GPA requirement, give full score
    no_req = min_gpas <= 0
    
    # Calculate ratio (avoid division by zero)
    safe_gpas = np.where(no_req, 1.0, min_gpas)
    scores = np.minimum(user_gpa / safe_gpas, 1.0)
    
    # No requirement = full score
    scores = np.where(no_req, 1.0, scores)
    
    return scores


def score_major(user_major, user_department, fields_list):
    """
    Score based on field-of-study match.
    
    - 1.0: user's major is in the scholarship's field list
    - 0.8: user's major isn't listed, but a related field in their department is
    - 0.5: scholarship is open to all fields (empty list)
    - 0.0: no match at all
    
    Args:
        user_major: str
        user_department: str
        fields_list: list of lists (each scholarship's eligible fields)
    
    Returns:
        numpy array of scores
    """
    # Department-to-fields mapping for partial matches
    dept_fields = {
        "Faculty of Science": ["Biology", "Chemistry", "Physics", "Mathematics", "Environmental Science"],
        "Faculty of Engineering": ["Engineering", "Computer Science"],
        "Faculty of Arts": ["Arts", "Communications", "Political Science", "Psychology", "Social Sciences"],
        "Faculty of Health Sciences": ["Health Sciences", "Nursing", "Kinesiology"],
        "School of Business": ["Business", "Economics"],
        "Faculty of Education": ["Education"],
        "Faculty of Law": ["Law"],
        "Faculty of Mathematics": ["Mathematics", "Computer Science"],
        "Faculty of Environment": ["Environmental Science"],
        "School of Computer Science": ["Computer Science", "Mathematics"],
    }
    
    dept_related = set(dept_fields.get(user_department, []))
    scores = np.zeros(len(fields_list), dtype=np.float64)
    
    for i, fields in enumerate(fields_list):
        if not fields:  # Open to all
            scores[i] = 0.5
        elif user_major in fields:  # Direct match
            scores[i] = 1.0
        elif dept_related.intersection(set(fields)):  # Department overlap
            scores[i] = 0.8
        else:
            scores[i] = 0.0
    
    return scores


def score_eligibility(user, eligibility_list):
    """
    Binary eligibility score across multiple criteria.
    
    Checks: education level, province, GPA minimum, demographics.
    Each passed check adds to the score proportionally.
    
    Args:
        user: User object
        eligibility_list: list of eligibility dicts
    
    Returns:
        numpy array of scores (0.0 - 1.0)
    """
    scores = np.zeros(len(eligibility_list), dtype=np.float64)
    
    for i, elig in enumerate(eligibility_list):
        checks_passed = 0
        total_checks = 0
        
        # Education level check
        ed_levels = elig.get("education_level", [user.education_level])
        total_checks += 1
        if user.education_level in ed_levels:
            checks_passed += 1
        
        # Province check
        provinces = elig.get("provinces", [user.province])
        total_checks += 1
        if user.province in provinces:
            checks_passed += 1
        
        # GPA check
        min_gpa = elig.get("min_gpa", 0)
        if min_gpa > 0:
            total_checks += 1
            if user.gpa >= min_gpa:
                checks_passed += 1
        
        # First-gen check
        if elig.get("first_gen", False):
            total_checks += 1
            if user.is_first_gen:
                checks_passed += 1
        
        # Minority check
        if elig.get("minority", False):
            total_checks += 1
            if user.is_minority:
                checks_passed += 1
        
        scores[i] = checks_passed / total_checks if total_checks > 0 else 1.0
    
    return scores


def score_deadline(deadlines):
    """
    Score based on time remaining until deadline.
    More time = higher score. Encourages applying to scholarships with
    comfortable timelines.
    
    - 180+ days remaining: 1.0
    - Scales linearly down to 0 days: 0.0
    
    Args:
        deadlines: numpy array of deadline dates (as timestamps)
    
    Returns:
        numpy array of scores (0.0 - 1.0)
    """
    today = np.datetime64(date.today())
    
    # Convert to numpy datetime if needed
    if not isinstance(deadlines, np.ndarray):
        deadlines = np.array(deadlines, dtype="datetime64[D]")
    
    days_remaining = (deadlines - today).astype("timedelta64[D]").astype(np.float64)
    
    # Normalize: 180 days = full score, 0 days = zero
    scores = np.clip(days_remaining / 180.0, 0.0, 1.0)
    
    return scores


def score_citizenship(user_citizenship, scholarship_requirements):
    """
    Score based on citizenship match.
    
    - 1.0: scholarship has no citizenship requirement, or user matches exactly
    - 0.5: scholarship accepts PR and user is PR
    - 0.0: user doesn't qualify
    
    Args:
        user_citizenship: str ("canadian", "permanent_resident", "international")
        scholarship_requirements: list of str
    
    Returns:
        numpy array of scores
    """
    scores = np.zeros(len(scholarship_requirements), dtype=np.float64)
    
    for i, req in enumerate(scholarship_requirements):
        if req == "any":
            scores[i] = 1.0
        elif req == "canadian":
            scores[i] = 1.0 if user_citizenship == "canadian" else 0.0
        elif req == "canadian_or_pr":
            if user_citizenship in ("canadian", "permanent_resident"):
                scores[i] = 1.0
            else:
                scores[i] = 0.0
        else:
            scores[i] = 0.5  # Unknown requirement, give partial credit
    
    return scores


def score_award_size(amounts_max):
    """
    Score based on award size using log scale.
    Larger awards score higher, but diminishing returns prevent
    $100k scholarships from completely dominating $5k ones.
    
    Args:
        amounts_max: numpy array of maximum award amounts
    
    Returns:
        numpy array of scores (0.0 - 1.0)
    """
    amounts = np.array(amounts_max, dtype=np.float64)
    
    # Avoid log(0)
    amounts = np.maximum(amounts, 1.0)
    
    # Log-normalized: score = log(amount) / log(max_amount)
    max_amount = np.max(amounts)
    if max_amount <= 1.0:
        return np.ones(len(amounts))
    
    scores = np.log(amounts) / np.log(max_amount)
    
    return np.clip(scores, 0.0, 1.0)


# ──────────────────────────────────────────────────────────────
# Main scoring engine
# ──────────────────────────────────────────────────────────────

def compute_scores(user, df, weights=None):
    """
    Compute weighted match scores for all scholarships against a user profile.
    
    Uses NumPy vectorized operations across six factors:
    GPA, Major, Eligibility, Deadline, Citizenship, Award Size.
    
    Args:
        user: User object
        df: Cleaned scholarship DataFrame
        weights: Optional dict of custom weights (must sum to ~1.0)
    
    Returns:
        numpy array of final weighted scores (0.0 - 1.0)
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    
    n = len(df)
    
    # Parse eligibility and fields from JSON strings
    eligibility_list = []
    fields_list = []
    min_gpas = np.zeros(n)
    
    for i, (_, row) in enumerate(df.iterrows()):
        # Parse eligibility
        elig = row["eligibility"]
        if isinstance(elig, str):
            elig = json.loads(elig)
        eligibility_list.append(elig)
        
        # Extract min_gpa
        min_gpas[i] = elig.get("min_gpa", 0)
        
        # Parse fields
        fields = row["field_of_studys"]
        if isinstance(fields, str):
            fields = json.loads(fields)
        fields_list.append(fields)
    
    # ── Compute individual factor scores ──
    gpa_scores = score_gpa(user.gpa, min_gpas)
    major_scores = score_major(user.major, user.department, fields_list)
    elig_scores = score_eligibility(user, eligibility_list)
    
    # Deadline scores
    deadline_vals = pd.to_datetime(df["deadline"]).values.astype("datetime64[D]")
    deadline_scores = score_deadline(deadline_vals)
    
    # Citizenship scores
    citizenship_reqs = df["citizenship_requirement"].tolist()
    citizenship_scores = score_citizenship(user.citizenship, citizenship_reqs)
    
    # Award size scores
    award_scores = score_award_size(df["amount_max"].values)
    
    # ── Weighted combination ──
    # Stack all scores into a matrix (n_scholarships x 6)
    score_matrix = np.column_stack([
        gpa_scores,
        major_scores,
        elig_scores,
        deadline_scores,
        citizenship_scores,
        award_scores
    ])
    
    # Weight vector
    weight_vector = np.array([
        weights["gpa"],
        weights["major"],
        weights["eligibility"],
        weights["deadline"],
        weights["citizenship"],
        weights["award_size"]
    ])
    
    # Weighted sum (matrix-vector multiplication)
    final_scores = score_matrix @ weight_vector
    
    # Normalize to 0-1 range
    final_scores = np.clip(final_scores, 0.0, 1.0)
    
    return final_scores, score_matrix, weight_vector


# ──────────────────────────────────────────────────────────────
# Custom merge sort
# ──────────────────────────────────────────────────────────────

def _merge(left, right, scores, deadlines):
    """
    Merge two sorted lists by score (descending).
    Ties broken by deadline urgency (sooner deadline first).
    """
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        li, rj = left[i], right[j]
        
        # Compare by score (descending)
        if scores[li] > scores[rj]:
            result.append(li)
            i += 1
        elif scores[li] < scores[rj]:
            result.append(rj)
            j += 1
        else:
            # Tie: sort by deadline (sooner first)
            if deadlines[li] <= deadlines[rj]:
                result.append(li)
                i += 1
            else:
                result.append(rj)
                j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(indices, scores, deadlines):
    """
    Custom merge sort implementation.
    Sorts scholarship indices by score descending, with deadline as tiebreaker.
    
    Args:
        indices: list of integer indices
        scores: numpy array of scores
        deadlines: numpy array of deadline values (for tiebreaking)
    
    Returns:
        Sorted list of indices
    """
    if len(indices) <= 1:
        return indices
    
    mid = len(indices) // 2
    left = merge_sort(indices[:mid], scores, deadlines)
    right = merge_sort(indices[mid:], scores, deadlines)
    
    return _merge(left, right, scores, deadlines)


def rank_scholarships(user, df, weights=None):
    """
    Score and rank all scholarships for a user.
    
    1. Computes weighted scores with NumPy
    2. Sorts with custom merge sort (descending score, deadline tiebreak)
    3. Returns ranked DataFrame with score columns
    
    Args:
        user: User object
        df: Cleaned scholarship DataFrame
        weights: Optional custom weights dict
    
    Returns:
        Ranked DataFrame with 'fit_score' column, score breakdown DataFrame
    """
    final_scores, score_matrix, weight_vector = compute_scores(user, df, weights)
    
    # Convert deadlines for tiebreaking
    deadlines = pd.to_datetime(df["deadline"]).values.astype("datetime64[D]")
    deadline_ints = deadlines.astype(np.int64)
    
    # Custom merge sort
    indices = list(range(len(df)))
    sorted_indices = merge_sort(indices, final_scores, deadline_ints)
    
    # Build ranked DataFrame
    ranked_df = df.iloc[sorted_indices].copy()
    ranked_df["fit_score"] = final_scores[sorted_indices]
    ranked_df["rank"] = range(1, len(ranked_df) + 1)
    
    # Add individual score breakdowns
    factor_names = ["gpa_score", "major_score", "eligibility_score",
                    "deadline_score", "citizenship_score", "award_score"]
    for j, name in enumerate(factor_names):
        ranked_df[name] = score_matrix[sorted_indices, j]
    
    ranked_df = ranked_df.reset_index(drop=True)
    
    return ranked_df


def display_top_matches(ranked_df, top_n=15):
    """
    Print a formatted table of top scholarship matches.
    
    Args:
        ranked_df: DataFrame from rank_scholarships()
        top_n: Number of results to display
    """
    top = ranked_df.head(top_n)
    
    print(f"\n   ╔══════════════════════════════════════════════════════════════════════════════════╗")
    print(f"   ║                          TOP {top_n} SCHOLARSHIP MATCHES                            ║")
    print(f"   ╚══════════════════════════════════════════════════════════════════════════════════╝")
    
    print(f"\n   {'Rank':<6}{'Score':<8}{'Amount':>10}  {'Deadline':<12}  {'Scholarship Name'}")
    print(f"   {'─'*6}{'─'*8}{'─'*10}  {'─'*12}  {'─'*44}")
    
    for _, row in top.iterrows():
        score_pct = f"{row['fit_score']*100:.1f}%"
        amount = f"${row['amount_max']:,.0f}"
        deadline = pd.to_datetime(row['deadline']).strftime('%Y-%m-%d')
        name = row['name'][:44]  # Truncate long names
        rank = int(row['rank'])
        
        # Color indicators based on score
        if row['fit_score'] >= 0.75:
            indicator = "★"
        elif row['fit_score'] >= 0.50:
            indicator = "●"
        else:
            indicator = "○"
        
        print(f"   {indicator} {rank:<4} {score_pct:<8}{amount:>10}  {deadline:<12}  {name}")
    
    print(f"\n   ★ = Excellent match (75%+)  ● = Good match (50-74%)  ○ = Partial match (<50%)")
    print(f"   Total scholarships scored: {len(ranked_df)}")
    
    # Score breakdown for #1 match
    if len(top) > 0:
        best = top.iloc[0]
        print(f"\n   ┌─── Score Breakdown: #{1} Match ───────────────────┐")
        print(f"   │  GPA Match:          {best['gpa_score']:.2f}  (weight: 0.25)     │")
        print(f"   │  Major Match:        {best['major_score']:.2f}  (weight: 0.20)     │")
        print(f"   │  Eligibility Match:  {best['eligibility_score']:.2f}  (weight: 0.20)     │")
        print(f"   │  Deadline Score:     {best['deadline_score']:.2f}  (weight: 0.10)     │")
        print(f"   │  Citizenship Match:  {best['citizenship_score']:.2f}  (weight: 0.10)     │")
        print(f"   │  Award Size Score:   {best['award_score']:.2f}  (weight: 0.15)     │")
        print(f"   │  ─────────────────────────────────────────────  │")
        print(f"   │  FINAL SCORE:        {best['fit_score']:.2f}                      │")
        print(f"   └────────────────────────────────────────────────┘")
