# conftest.py file contains fixtuxes and makes it accessible in package level scope 
# without specifically importing 

from fastapi.testclient import TestClient
from app.main import app
from app import database_orm, schemas, config, models
from urllib.parse import quote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest


SQLALCHEMY_DATABASE_URL = f"postgresql://{config.settings.DB_USERNAME}:%s@{config.settings.DATABASE_HOSTNAME}/{config.settings.DB_NAME}-test"

engine = create_engine(SQLALCHEMY_DATABASE_URL % quote(config.settings.DB_PASSWORD))

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    print("my session fixture ran")
    database_orm.Base.metadata.drop_all(bind=engine)
    database_orm.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

#client Fixture to delete all data before testing and return TestClient
@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[database_orm.get_db] = override_get_db
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
    #print(f"DEKHO LOGIN - {login_user.json()} DEKHO LOGIN TYPE - {login_user}")
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
def create_posts(create_test_user, client, session):
    usersid_data = {"email": create_test_user['email'], "adminToken": config.settings.ADMIN_TOKEN_FOR_SANITY}
    user_id = client.post("/usersid/", json=usersid_data)
    #print(f"DEKHO USERID - {user_id.json()['id']}")
    get_user_id = user_id.json()['id']
    #print(f"DEKHO - {user_id.json()} TYPE - {type(user_id)}")
    #get_user_id = schemas.UserId(**user_id.json())

    session.add_all([models.Post(title="1st title dekho", content="1st ka content", user_id=get_user_id),
                    models.Post(title="2nd title dekho", content="2nd ka content", user_id=get_user_id), 
                    models.Post(title="3rd title dekho", content="3rd ka content", user_id=get_user_id)])
    
    session.commit()
    posts_record = session.query(models.Post).all()
    #print(f"DEKHO POST KA ID - {(posts_record[0].id)}")
    return posts_record 

@pytest.fixture
def create_posts_user2(create_test_user2, client, session):
    usersid_data = {"email": create_test_user2['email'], "adminToken": config.settings.ADMIN_TOKEN_FOR_SANITY}
    user_id = client.post("/usersid/", json=usersid_data)
    get_user_id = user_id.json()['id']
    #get_user_id = schemas.UserId(**user_id.json())

    session.add_all([models.Post(title="1st title dekho", content="4th ka content", user_id=get_user_id),
                    models.Post(title="2nd title dekho", content="5th ka content", user_id=get_user_id), 
                    models.Post(title="3rd title dekho", content="6th ka content", user_id=get_user_id)])
    
    session.commit()
    posts_record = session.query(models.Post).all()
    #print(f"DEKHO POST KA ID - {(posts_record[0].id)}")
    return posts_record