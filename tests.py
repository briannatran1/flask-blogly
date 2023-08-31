from models import DEFAULT_IMAGE_URL, User, Post
from app import app, db
from unittest import TestCase
import os

# make separate db for tests!
os.environ["DATABASE_URL"] = "postgresql:///blogly_test"


# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        # As you add more models later in the exercise, you'll want to delete
        # all of their records before each test just as we're doing with the
        # User model below.
        User.query.delete()

        self.client = app.test_client()

        test_user = User(
            first_name="test1_first",
            last_name="test1_last",
            image_url=None,
        )


        db.session.add(test_user)
        db.session.commit()


        # We can hold onto our test_user's id by attaching it to self (which is
        # accessible throughout this test class). This way, we'll be able to
        # rely on this user in our tests without needing to know the numeric
        # value of their id, since it will change each time our tests are run.
        self.user_id = test_user.id

        test_post = Post(
            title="test1_title",
            content="test1_content",
            user_id=self.user_id
        )

        db.session.add(test_post)
        db.session.commit()

        self.post_id = test_post.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_list_users(self):
        """Shows list of users"""
        with self.client as c:
            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)

    def test_show_user_form(self):
        """Shows creating a new user form"""
        with self.client as c:
            resp = c.get("/users/new")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Create a user", html)
            self.assertIn("<form", html)

    def test_show_user_info(self):
        """Shows information about a given user"""
        with self.client as c:
            resp = c.get(f"/users/{self.user_id}")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)

            self.assertIn('test1_first', html)
            self.assertIn('test1_last', html)

    def test_show_edit_page(self):
        """Make sure edit page is shown for user"""
        with self.client as c:
            resp = c.get(f"/users/{self.user_id}/edit")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)

            self.assertIn('Edit a user', html)

    def test_delete_user_and_redirect(self):
        """Makes sure user is redirected to user listing after deleting"""
        with self.client as c:
            resp = c.post(f"/users/{self.user_id}/delete",
                          data={"user_id": self.user_id})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, '/')

    def test_redirection_followed(self):
        """Confirms redirection"""
        with self.client as c:
            resp = c.get('/', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Users', html)

    def test_create_new_user(self):
        """Creates a new user"""
        with self.client as c:
            resp = c.post('/users/new',
                          data={"first_name": 'Chris',
                                "last_name": 'Alley'},
                                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Chris', html)
            self.assertIn('Alley', html)

    # def test_handle_new_post_form(self):
    #     """Tests handling of new post form"""
    #     with self.client as c:
    #         resp = c.post(f'/users/{self.user_id}/posts/new',
    #                       data={
    #                           'title': 'Very cool post',
    #                           'content': 'This is some amzing content'
    #                       },
    #                       follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Very cool post', html)

            # resp = c.post(f'/users/{self.user_id}/posts/new',
            #               data={
            #                   'title': 'Such wow post',
            #                   'content': 'This is some amzing content'
            #               },
            #               follow_redirects=True)
            # html = resp.get_data(as_text=True)

            # self.assertEqual(resp.status_code, 200)
            # self.assertIn('Such wow post', html)
    def test_show_add_post_form(self):
        """Tests showing user the add post form"""
        with self.client as c:
            resp = c.get(f'/users/{self.user_id}/posts/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add Post for', html)
            self.assertIn('test1_first', html)
            self.assertIn('test1_last', html)

    def test_show_post_edit_form(self):
        """Tests showing edit post form for specified post"""
        with self.client as c:
            resp = c.get(f'/posts/{self.post_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit Post', html)