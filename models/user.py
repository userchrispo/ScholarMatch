
import json

class User:
    def __init__(self, name, email, education_level, major, gpa, year, province, demographics, activities, department, citizenship="canadian"):

        valid_education = ["highschool", "university", "college"]
        valid_province = ["ontario"]
        valid_citizenship = ["canadian", "permanent_resident", "international"]

        if education_level.lower() not in valid_education:
            raise ValueError(f"Educational Levels must be one of: {valid_education}")
        
        if province.lower() not in valid_province:
            raise ValueError(f"Must live in one of these provnices: {valid_province}")
            
        if not (0.0 <= gpa <= 4.0):
            raise ValueError("GPA must be between 0.0 and 4.0")

        if citizenship.lower() not in valid_citizenship:
            raise ValueError(f"Citizenship must be one of: {valid_citizenship}")
            
        self.name = name
        self.email = email
        self.education_level = education_level
        self.major = major
        self.gpa = gpa 
        self.year = year
        self.province = province
        self.demographics = demographics
        self.activities = activities
        self.department = department
        self.citizenship = citizenship.lower()

    def to_dict(self):
       return  {
            "name": self.name,
            "email": self.email,
            "education_level": self.education_level,
            "major": self.major,
            "gpa": self.gpa,
            "year": self.year,
            "province": self.province,
            "demographics": self.demographics,
            "activities": self.activities,
            "department": self.department,
            "citizenship": self.citizenship
        }
    
    @classmethod
    def from_dict(cls, stats):
        return cls(
            stats["name"], stats["email"], stats["education_level"],
            stats["major"], stats["gpa"], stats["year"], stats["province"],
            stats["demographics"], stats["activities"], stats["department"],
            stats.get("citizenship", "canadian")
        )


    def save_stats(self, filepath):

        with open(filepath, "w") as file:
            json.dump(self.to_dict(), file, indent=4)
    
    @classmethod
    def load_stats(cls, filepath):
        try:
            with open(filepath, "r") as file:
                stats = json.load(file)
        except FileNotFoundError:
            print("FILE NOT FOUND, PLEASE CREATE A USER BEFORE TRYING TO LOAD USERS")
            return None
        
        user = cls.from_dict(stats)
        return user

    @property
    def is_first_gen(self):
        return self.demographics.get("first_gen", False)

    @property
    def is_minority(self):
        return self.demographics.get("minority", False)

    @property
    def has_disability(self):
        return self.demographics.get("disabled", False)

    def __repr__(self):
        return (f"User(name='{self.name}', email='{self.email}', education_level='{self.education_level}', "
                f"major='{self.major}', gpa={self.gpa}, year={self.year}, province='{self.province}', "
                f"citizenship='{self.citizenship}', department='{self.department}')")
