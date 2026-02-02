USER Use cases

MAIN MENU
1. Create New User
2. Login With Profile


1. User First time using no profile

Chooses Create New user
Ask user info(name,email,gpa,major,ex..)
Intalize an user object with this information and creates user profile >
user saves profile to json file for future use

user create user object
to save user object we convert it to a dict using to_dict
we than save it in json file


2.  User already has a profile 

Chooses login with profile 
User enters filepath
call loadstats  return user profile object

what happens under the hood
loadstats function gets the dict(which contains name,emaill ex....) from a json file
store it in a variable, call from_dict() function which turns the dict to user object




demographics: age, firstgen, background, miniorites 