from django.test import TestCase
from rest_framework.test import APIRequestFactory
from marco_polo.models import User, UserProfile
from rest_framework.test import force_authenticate


# Create your tests here.

class TestUpdatUser(TestCase):

    def setUp(self): 
        User.objects.create_user(username="TestPerson", email="testperson@gmail.com", password= "password")
        user = User.objects.get(username='TestPerson')

    def testchangeemail(self):
        """factory = APIRequestFactory
        user = User.objects.get(username='TestPerson') 
        request = factory.put(path='/user/settings/',data={'username': 'testperson2@gmail.com'}, format='json') """
        newemail = "testperson2@gmail.com"
        user = User.objects.get(username='TestPerson') 
        user.email = newemail
        user.save()
        user2 = User.objects.get(username='TestPerson')
        self.assertEqual(user2.email, newemail)

    def testchangepassword(self): 
        newpassword = "password1"
        user = User.objects.get(username='TestPerson') 
        user.password = newpassword
        user.save()
        user2 = User.objects.get(username='TestPerson')
        self.assertEqual(user2.password, newpassword)

    def testadduser(self):
        User.objects.create_user(username="TestPerson2", email="testperson2@gmail.com", password= "password")
        try:
            user = User.objects.get(username='TestPerson2')
        except User.DoesNotExist:
            self.assertEqual("hello","heeelo")
        
