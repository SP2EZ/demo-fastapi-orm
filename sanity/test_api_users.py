from app import schemas, config
from jose import jwt
import pytest


def test_root_path(client):
    root_response = client.get("/")
    #print(root_response.json())
    assert 'Hello, you have reached API Default Path' in root_response.json().get('message')
    assert root_response.status_code == 200

def test_create_user(client):
    # Path "/users" doesn't work, instead use "/users/"
    # Reason is FastAPI redirects all requests for /users to /users/ automatically
    # and the status code for redirecting is 307 this is cause problem with our assert commands
    create_user = client.post("/users/", json={"email": "test@email.com", "password": "pasword123"})
    #print(create_user.json())
    # Unpacking the json object to python object so that it can validated via pydantic models
    create_user_response = schemas.UserResponse(**create_user.json())
    assert create_user_response.email == "test@email.com"
    assert create_user.status_code == 201

# create_test_user is fixture that creates a user before authentication is tested
def test_login_user(create_test_user, client):
    login_user = client.post("/login/", data={"username": create_test_user['email'], "password": create_test_user['password']})
    login_user_response = schemas.Token(**login_user.json())
    #print(f"Dekho - {login_user_response}")
    payLoad = jwt.decode(login_user_response.access_token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM])
    #user_id = payLoad.get("user_id")
    assert payLoad.get("user_id") is not None
    assert login_user.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [
    ('test@email.com', 'pasword123', 200),
    ('galat@email.com', 'galatpassword', 403),
    ('test@email.com', 'galatpassword', 403),
    (None, 'galatpassword', 422),
    ('galat@email.com', None, 422)
])
def test_incorrect_login(create_test_user, client, email, password, status_code):
    login_user = client.post("/login/", data={"username": email, "password": password})
    assert login_user.status_code == status_code


def test_create_posts(authenticate_test_user):
    create_posts = authenticate_test_user.post("/posts/", json={"title": "1st title dekho", "content": "1st ka content", "published": "True"})
    #print(create_posts.json())
    create_posts_response = schemas.PostResponse(**create_posts.json())
    assert create_posts_response.title == "1st title dekho"
    assert create_posts.status_code == 201

def test_get_posts(create_posts, authenticate_test_user):
    get_posts = authenticate_test_user.get("/posts/?limit=1&skip=0&search=3rd")
    print(get_posts.json()[0])
    get_posts_response = schemas.PostResponseWithLikes(**get_posts.json()[0])
    assert get_posts.status_code == 200
    assert get_posts_response.title == '3rd title dekho'
    assert get_posts_response.published != 'True'

def test_unauthorized_get_posts(create_test_user, client):
    get_posts =client.get("/posts/?limit=1&skip=0&search=3rd")
    assert get_posts.status_code == 401


def test_get_posts_by_id(create_posts, authenticate_test_user):
    #print(f"LOOKATME {create_posts}")
    get_correct_posts_by_id = authenticate_test_user.get(f"/posts/{create_posts[0].id}")
    get_incorrect_posts_by_id = authenticate_test_user.get(f"/posts/{create_posts[0].id + 5000}")
    assert get_correct_posts_by_id.status_code == 200
    assert get_incorrect_posts_by_id.status_code == 404

def test_unauthorized_get_posts_by_id(create_posts, client):
    get_correct_posts_by_id = client.get(f"/posts/{create_posts[0].id}")
    #print(f"LOOATME {get_correct_posts_by_id.json()}")
    assert get_correct_posts_by_id.status_code == 401

def test_delete_post(authenticate_test_user, create_posts):
    #print(f"USER1 POST - {create_posts}\nUSER2 POST - {create_posts[0].id}")
    delete_post = authenticate_test_user.delete(f"/posts/{create_posts[0].id}")   
    assert delete_post.status_code == 204
    
def test_delete_unavailable_post(authenticate_test_user, create_posts):
    delete_unavailable_post = authenticate_test_user.delete(f"/posts/{create_posts[0].id + 5000}")
    assert delete_unavailable_post.status_code == 404

def test_delete_other_user_post(authenticate_test_user, create_posts_user2):
    #print(f"USER1 POST - {create_posts_user2}\nUSER2 POST - {create_posts_user2[0].id}")
    delete_other_user_post = authenticate_test_user.delete(f"/posts/{create_posts_user2[0].id}")
    assert delete_other_user_post.status_code == 404

def test_unauthorized_delete_post(create_posts, client):
    unauthorized_delete_post = client.delete(f"/posts/{create_posts[0].id}")
    assert unauthorized_delete_post.status_code == 401


def test_update_post(authenticate_test_user, create_posts):
    data = {
        "title": "update dekho", "content": "updated content", "published": "False"
    }
    update_post = authenticate_test_user.put(f"/posts/{create_posts[0].id}", json=data)
    update_post_response = schemas.PostResponse(**update_post.json())
    update_non_existing_post = authenticate_test_user.put(f"/posts/{create_posts[0].id + 5000}", json=data)
    assert update_post.status_code == 200
    assert update_post_response.title == data['title']
    assert update_non_existing_post.status_code == 404

def test_update_other_user_post(authenticate_test_user, create_posts_user2):
    data = {
        "title": "update dekho", "content": "updated content", "published": "False"
    }
    update_other_user_post = authenticate_test_user.put(f"/posts/{create_posts_user2[0].id}", json=data)
    assert update_other_user_post.status_code == 404

def test_unauthorized_update_post(create_posts, client):
    data = {
        "title": "update dekho", "content": "updated content", "published": "False"
    }
    unauthorized_update_post = client.put(f"/posts/{create_posts[0].id}", json=data)
    assert unauthorized_update_post.status_code == 401


def test_vote_post(create_posts, authenticate_test_user):
    vote_post = authenticate_test_user.post(f"/votes/", json={"post_id": create_posts[0].id, "vote_dir": 1})
    #print(f"LOOATME VOTE - {vote_post.json()} post_id - {create_posts[0]['id']}")
    vote_non_existing_post = authenticate_test_user.post(f"/votes/", json={"post_id": int(create_posts[0].id + 5000), "vote_dir": 1})
    vote_post_twice = authenticate_test_user.post(f"/votes/", json={"post_id": create_posts[0].id, "vote_dir": 1})
    #print(f"Vote Twice - {vote_post_twice.json()}")
    unvote_post = authenticate_test_user.post(f"/votes/", json={"post_id": create_posts[0].id, "vote_dir": 0})   
    assert vote_post.status_code == 200
    assert vote_non_existing_post.status_code == 404
    assert vote_post_twice.status_code == 409
    assert unvote_post.status_code == 200
    

def test_unauthorized_vote(create_posts, client):
    unauthorized_vote = client.post(f"/votes/", json={"post_id": create_posts[0].id, "vote_dir": 1})
    assert unauthorized_vote.status_code == 401
