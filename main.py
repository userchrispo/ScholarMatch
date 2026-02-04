from models.user import User
from models.scholarship import Scholarship


def display_menu():
    print("\n═══════════════════════════════════════════════════")
    print("\n🎓 SCHOLARSHIP FINDER 🎓\n")
    print("═══════════════════════════════════════════════════")
    print("\n[1]  Create New Profile")
    print("\n[2]  Load Exisitng Profile")
    print("\n[3]  EXIT")


def create_user():
    pass


def load_user():
    pass


def search_scholarships(user):
    pass






def main():

    display_menu()
    try: 
        choice = int(input("\n1 - 2 - 3: "))
    except ValueError:
        print("\nENTER ONE OF THE FOLLOWING 1 - 2 - 3")
        return None

    if choice == 1:
        print(choice)
    
    elif choice == 2:
        print(choice)
    
    elif choice == 3:
        print("\nThank you for trying ScholarMatch, Hope you enjoyed and found some scholarships!!!!!")
        return None
    else:
        pprint("\nENTER ONE OF THE FOLLOWING 1 - 2 - 3")
        return None


if __name__ == "__main__":
    main()