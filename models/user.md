# User Module Design

The User class represents a student profile for scholarship matching.

# User Flows

# Flow 1: New User (No Profile)

1. User selects **"Create New User"** from main menu
2. gives prompts for: name, email, GPA, major, province, demographics, activities, department
3. System validates input (GPA 0-4, valid province, valid education level)
4. Creates `User` object with provided data
5. User provides filepath (e.g., `data/user_profiles/ladoLogga.json`)
6. Calls `user.save_stats(filepath)` to persist to JSON

**Under the hood:**

- `save_stats()` calls `to_dict()` to convert User → dictionary
- Dictionary is written to JSON file via `json.dump()`

---

# Flow 2: Returning User (Has Profile)

1. User selects **"Login with Profile"** from main menu
2. User provides filepath to their saved profile
3. System calls `User.load_stats(filepath)`
4. Returns populated User object

**Under the hood:**

- `load_stats()` reads JSON file → dictionary
- Calls `from_dict()` to convert dictionary → User object
- Returns the User object

## Class Methods Summary

| Method           | Type        | Purpose                         |
| ---------------- | ----------- | ------------------------------- |
| `__init__()`     | Instance    | Create user with validation     |
| `to_dict()`      | Instance    | Convert user to dictionary      |
| `from_dict()`    | Classmethod | Create user from dictionary     |
| `save_stats()`   | Instance    | Save user to JSON file          |
| `load_stats()`   | Classmethod | Load user from JSON file        |
| `is_first_gen`   | Property    | Check first-gen status          |
| `is_minority`    | Property    | Check minority status           |
| `has_disability` | Property    | Check disability status         |
| `__repr__()`     | Instance    |  print user for debugging       |
