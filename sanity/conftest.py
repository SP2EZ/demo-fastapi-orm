# conftest.py file contains fixtuxes and makes it accessible in package level scope 
# without specifically importing 

from fastapi.testclient import TestClient
from app.main import app
from app import database, schemas
import pytest


#client = TestClient(app)

#client Fixture to delete all data before testing and return TestClient
@pytest.fixture
def client():
    database.cursor.execute(""" DELETE FROM votes """)
    database.cursor.execute(""" DELETE FROM posts """)   
    database.cursor.execute(""" DELETE FROM users """)
    
    database.conn.commit()
    yield TestClient(app)

@pytest.fixture
def create_test_user(client):
    login_data = {"email": "test@email.com", "password": "pasword123"}
    create_user = client.post("/users/", json=login_data)
    create_user_response = schemas.UserResponse(**create_user.json())
    assert create_user_response.email == "test@email.com"
    assert create_user.status_code == 201
    updated_user = create_user.json()
    updated_user['password'] = login_data['password']
    return updated_user

@pytest.fixture
def create_test_user2(client):
    login_data = {"email": "test1@email.com", "password": "pasword123"}
    create_user = client.post("/users/", json=login_data)
    create_user_response = schemas.UserResponse(**create_user.json())
    assert create_user_response.email == "test1@email.com"
    assert create_user.status_code == 201
    updated_user = create_user.json()
    updated_user['password'] = login_data['password']
    return updated_user
    
@pytest.fixture
def authenticate_test_user(create_test_user, client):
    login_user = client.post("/login/", data={"username": create_test_user['email'], "password": create_test_user['password']})
    login_user_response = schemas.Token(**login_user.json())
    #print(f"Dekho - {login_user_response}")
    #payLoad = jwt.decode(login_user_response.access_token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM])
    #user_id = payLoad.get("user_id")
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {login_user_response.access_token}"
        }
    return client

@pytest.fixture
def create_posts(create_test_user):
    get_user_id = database.cursor.execute(""" SELECT * FROM users WHERE email = %s""", (create_test_user['email'],)).fetchone()
    posts_record = database.cursor.execute(""" 
    INSERT INTO posts (title, content, published, user_id) 
    VALUES 
    ('1st title dekho', '1st ka content', True, %s),
    ('2nd title dekho', '2nd ka content', False, %s),
    ('3rd title dekho', '3rd ka content', True, %s)
    RETURNING * 
    """, (get_user_id['id'], get_user_id['id'], get_user_id['id'])).fetchall()
    database.conn.commit()
    # create_post_response = authenticate_test_user.post("/posts/", json={"title": "1st title dekho", "content": "1st ka content", "published": "True"})
    # authenticate_test_user.post("/posts/", json={"title": "2nd title dekho", "content": "2nd ka content"})
    # authenticate_test_user.post("/posts/", json={"title": "3rd title dekho", "content": "3rd ka content", "published": "False"})
    return posts_record 

@pytest.fixture
def create_posts_user2(create_test_user2):
    get_user_id = database.cursor.execute(""" SELECT * FROM users WHERE email = %s""", (create_test_user2['email'],)).fetchone()
    posts_record = database.cursor.execute(""" 
    INSERT INTO posts (title, content, published, user_id) 
    VALUES 
    ('1st title dekho', '4th ka content', True, %s),
    ('2nd title dekho', '5th ka content', False, %s),
    ('3rd title dekho', '6th ka content', True, %s)
    RETURNING * 
    """, (get_user_id['id'], get_user_id['id'], get_user_id['id'])).fetchall()
    database.conn.commit()
    return posts_record 