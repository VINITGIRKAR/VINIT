# Sample data storage
users = []

# CREATE
def create_user(user_id, name, email):
    users.append({'id': user_id, 'name': name, 'email': email})
    print(f"User {name} added successfully.")

# READ
def read_users():
    if not users:
        print("No users found.")
    for user in users:
        print(user)

# UPDATE
def update_user(user_id, name=None, email=None):
    for user in users:
        if user['id'] == user_id:
            if name:
                user['name'] = name
            if email:
                user['email'] = email
            print(f"User {user_id} updated.")
            return
    print("User not found.")

# DELETE
def delete_user(user_id):
    global users
    users = [user for user in users if user['id'] != user_id]
    print(f"User {user_id} deleted.")

# Usage
create_user(1, "Alice", "alice@example.com")
create_user(2, "Bob", "bob@example.com")

print("\nAll users:")
read_users()

update_user(1, name="Alicia")

print("\nAfter update:")
read_users()

delete_user(2)

print("\nAfter deletion:")
read_users()
