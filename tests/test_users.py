import os
import unittest
import datetime

from project import app, db, bcrypt
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'

class UsersTests(unittest.TestCase): 

    # setup and teardown
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()
        
        self.assertEquals(app.debug, False)
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
    # helper functions
    def login(self,name,password):
        return self.app.post('/', data=dict(name=name,password=password), follow_redirects=True)
        
    def register(self,name,email,password,confirm):
        return self.app.post('register/', data=dict(name=name,email=email,password=password,confirm=confirm), follow_redirects=True)
        
    def logout(self):
        return self.app.get('logout/', follow_redirects=True)
        
    def create_user(self,name,email,password):
        new_user = User(name=name,email=email,password=bcrypt.generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
    def create_task(self):
        return self.app.post('add/', data=dict(name='Go to the bank',
                                               due_date = datetime.datetime.now(),
                                               priority = '1',
                                               posted_date = datetime.datetime.now(),
                                               status = '1'
                                               ),
                                     follow_redirects = True)
    # tests
    def test_users_can_register(self):
        new_user = User('James', 'johnjames@jj.org', bcrypt.generate_password_hash('totallyas11'))
        db.session.add(new_user)
        db.session.commit()
        data = db.session.query(User).all()
        for row in data:
            row.name
        assert row.name == 'James'
        
    def test_form_is_present_on_login_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please sign in to access your task list', response.data)
        
    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo','bar')
        self.assertIn(b'Invalid username or password', response.data)
    
    def test_users_can_login(self):
        self.register('Charlie', 'dirtgrub@asip.org', 'randpass01', 'randpass01')
        response = self.login('Charlie', 'randpass01')
        self.assertIn(b'Welcome', response.data)
        
    def test_invalid_form_data(self):
        self.register('Michael', 'mscott@dm.org', 'testpass01', 'testpass01')
        response = self.login('alert("alert_box");', 'foo')
        self.assertIn(b'Invalid username or password', response.data)
        
    def test_form_is_present_on_register_page(self):
        response = self.app.get('register/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access the task list', response.data)
    
    def test_user_registeration(self):
        self.app.get('register/', follow_redirects=True)
        response = self.register('John01', 'jdickens@jd.org', 'realpython01', 'realpython01')
        self.assertIn(b'Thanks for registering. Please login', response.data)
    
    def test_user_registeration_error(self):
        self.app.get('register/', follow_redirects=True)
        self.register('StanSmith', 'ssmith@cia.org', 'amdadrules33', 'amdadrules33')
        self.app.get('register/', follow_redirects=True)
        response = self.register('StanSmith', 'ssmith@cia.org', 'amdadrules33', 'amdadrules33')
        self.assertIn(b'That username and/or email already exist', response.data)    
        
    def test_logged_in_users_can_logout(self):
        self.register('Sasquatch', 'squatch@squatchin.org', 'sillysquatch02', 'sillysquatch02')
        self.login('Sasquatch','sillysquatch02')
        response = self.logout()
        self.assertIn(b'Goodbye!', response.data)
    
    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b'Goodbye', response.data)
    
    def test_user_login_field_errors(self):
        response = self.app.post(
            '/',
            data=dict(
                name='',
                password='python101',
            ),
            follow_redirects=True
        )
        self.assertIn(b'This field is required.', response.data)

    def test_string_representation_of_the_user_object(self):

        db.session.add(
            User(
                "Johnny",
                "john@doe.com",
                "johnny"
            )
        )

        db.session.commit()

        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(user.name, 'Johnny')

    def test_default_user_role(self):

        db.session.add(
            User(
                "Johnny",
                "john@doe.com",
                "johnny"
            )
        )

        db.session.commit()

        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(user.role, 'user')


if __name__ == "__main__":
    unittest.main()