# Scholarship Module Design

## Overview

The Scholarship class represents a scholarship opportunity with eligibility criteria and award details.

## Data Flow

### Loading Scholarships (from API/Cache)

1. `data_loader.py` fetches scholarships from CareerOneStop API
2. Data is loaded into Pandas DataFrame
3. Each row is converted to `Scholarship` object using `from_dict()`
4. Scholarships are cached to CSV for offline use

**Under the hood:**

- `from_dict()` takes a dictionary and creates a Scholarship instance
- `to_dict()` converts Scholarship back to dictionary for caching

### Checking Eligibility

1. For each scholarship, call `scholarship.is_eligible(user)`
2. Method checks all hard requirements:
   - Education level match
   - Major in allowed fields (or open to all)
   - GPA meets minimum
   - Province is allowed
   - Deadline not passed
   - Demographic requirements (first_gen, minority)
3. Returns `True` if ALL checks pass, `False` otherwise




## Class Methods Summary

| Method              | Type        | Purpose                            |
| ------------------- | ----------- | ---------------------------------- |
| `__init__()`        | Instance    | Create scholarship with validation |
| `is_eligible(user)` | Instance    | Check if user qualifies            |
| `to_dict()`         | Instance    | Convert to dictionary              |
| `from_dict()`       | Classmethod | Create from dictionary             |
| `is_open`           | Property    | Check if deadline hasn't passed    |
| `__repr__()`        | Instance    |  print for debugging               |

