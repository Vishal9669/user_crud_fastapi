from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel , Field # used for validation 
from typing import Optional # used for validation 

# Handling error's for users   
def ensure_username_in_db(username: str):
   if username not in user_db:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'username {username} not found') # Raise error if user not in user_db
     
#static user
user_db = {'Vishal': {'Username':'Vishal', 'age':24, 'location':'Khargone'}, 'Mohit': {'Username':'Mohit', 'age':22, 'location':'Indore'}, 'Mayank': {'Username':'Mayank', 'age':23, 'location':'Khargone'}}

# for adding dynamic user with validation
class User(BaseModel):
   username : str = Field(min_length=3, max_length=20)
   age: int = Field(None, gt=5, lt= 130)
   location : Optional[str] = None
   
class UserUpdate(User):
   age: int = Field(None, gt=5, lt= 200)
   
app = FastAPI()

#Query parameter
@app.get('/users')
def get_users_query(limit: int=20):
   user_list = list(user_db.values())
   return user_list[:limit]

# filter for specific user
@app.get('/users/{username}')
def get_users_path(username : str):
   ensure_username_in_db(username)
   return user_db[username]

# Add user request 
@app.post('/users')
def create_user(user: User):
   username = user.username
   if username in user_db:
      raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f'cannot create user. username {username} already exists.')    # Raise error response if user already exists
   user_db[username] = user.dict()
   return {"message": f'Successfully created user: {username}'}

# Update User
@app.put("/users")
def update_user(user: User):
   username = user.username
   ensure_username_in_db(username)
   user_db[username] = user.dict()
   return {"message" : f'Successfully updated user: {username}'}

# Update User partial
@app.patch("/users")
def update_user_partial(user: UserUpdate):
   username = user.username
   ensure_username_in_db(username)
   user_db[username].update(user.dict(exclude_unset=True))
   return {"message" : f'Successfully updated user: {username}'}
   

# Delete User
@app.delete('/users')
def delete_user(username: str):
   ensure_username_in_db(username)
   del user_db[username]
   return {"message": f'Successfully deleted user : {username}'}

