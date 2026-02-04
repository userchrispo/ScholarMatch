
from models.user import User
from models.scholarship import Scholarship
import pandas as pd


def load_from_api():
    pass


def cache_to_csv(df,filepath):
    df.to_csv(filepath,index=False)
    return



def load_from_cache(filepath):
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print("Cache not found, ISSUE WITH API")
        return None

    return df


def convert_to_scholarship(df):

    scholarships = []
    for row in  df.to_dict('records'):
        scholarship = Scholarship.from_dict(row)
        scholarships.append(scholarship)

    return scholarships