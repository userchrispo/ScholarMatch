from datetime import date
import json


class Scholarship:
    def __init__(self,id,name,provider,amount_min,amount_max,deadline,eligibility,field_of_studys,url,description):
        if (amount_min <= 0) or (amount_max <= 0):
            raise ValueError("SCHOLARSHIPS MUST PROVIDE MONEY")

        if (amount_min > amount_max):
            raise ValueError("amount_min cannot exceed amount_max")
        
        if (deadline < date.today()):
            raise ValueError("Scholarships must be appliable")
        
        self.id = id
        self.name = name
        self.provider = provider
        self.amount_min = amount_min
        self.amount_max = amount_max
        self.deadline = deadline
        self.eligibility = eligibility
        self.field_of_studys = field_of_studys
        self.url = url
        self.description = description

    
    def is_eligible(self,user):

        if user.education_level not in self.eligibility.get("education_level",[user.education_level]):
            return False
        if self.field_of_studys and user.major not in self.field_of_studys:
            return False
        if not user.gpa >= self.eligibility.get("min_gpa",0):
            return False
        if user.province not in self.eligibility.get("provinces",[user.province]):
            return False
        if (self.deadline < date.today()):
            return False
        if self.eligibility.get("first_gen",False) and  not user.is_first_gen:
            return False
        if self.eligibility.get("minority",False) and  not user.is_minority:
            return False
        
        
        return True

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "amount_min": self.amount_min,
            "amount_max": self.amount_max,
            "deadline": self.deadline,
            "eligibility": self.eligibility,
            "field_of_studys": self.field_of_studys,
            "url": self.url,
            "description": self.description
        }
    

    @classmethod
    def from_dict(cls,data):

        return cls(data["id"], data["name"], data["provider"], data["amount_min"], data["amount_max"], data["deadline"], data["eligibility"], data["field_of_studys"], data["url"], data["description"])
    

    @property
    def is_open(self):
        return self.deadline >= date.today()
    









    def __repr__(self):
        return f"Scholarship(name='{self.name}', amount$='{self.amount_max}', deadline='{self.deadline}', eligibility='{self.eligibility}"
        

        
        
        