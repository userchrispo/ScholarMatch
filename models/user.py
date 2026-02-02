
import json

class User:
    def __init__(self, name, email,education_level, major,gpa, province,demographics,activities):

        valid_education = ["highschool", "university", "college"]
        valid_province = ["ontario"]
        if education_level.lower() not in valid_education:
            raise ValueError(f"Educational Levels must be one of: {valid_education}")
            return None

        if province.lower() not in valid_province:
            raise ValueError(f"Must live in one of these provnices: {valid_province}")
            return None
        
        if not (0.0 <= gpa <= 4.0):
            raise ValueError("GPA must be between 0.0 and 4.0")
            return None
        
        self.name = name
        self.email = email
        self.education_level = education_level
        self.major = major
        self.gpa = gpa 
        self.province = province
        self.demographics = demographics
        self.activities = activities

    def to_dict(self):
       return  {
            "name": self.name,
            "email": self.email,
            "education_level": self.education_level,
            "major": self.major,
            "gpa": self.gpa,
            "province": self.province,
            "demographics": self.demographics,
            "activities": self.activities
        }
    
    @classmethod
    def from_dict(cls,stats):
        return cls(stats["name"], stats["email"], stats["education_level"], stats["major"], stats["gpa"], stats["province"], stats["demographics"], stats["activities"]
        )


    def save_stats(self, filepath):

        with open(filepath,"w") as file:
            json.dump(self.to_dict(),file,indent=4)
    
    @classmethod
    def load_stats(cls,filepath):
        try:
            with open(filepath,"r") as file:
                stats = json.load(file)
        except FileNotFoundError:
            print("FILE NOT FOUND, PLEASE CREATE A USER BEFORE TRYING TO LOAD USERS"
            )
            return None
       
        return cls.from_dict(stats)

    @property
    def is_first_gen(self):
    return self.demographics.get("first_gen",False)

    @property
    def is_miniority(self)
    return self.demographics.get("miniority",False)

    @property
    def has_disability(self)
    return self.demographics.get("disabled",False)


    def __repr__(self):
        return f"Usr(name='{self.name}', email='{email}',educational_level='{education_level}',  major='{self.major}', gpa='{gpa}', province='{province}', demographics='{demographics}', activities='{activities}')"


    















    

    
