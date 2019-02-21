from django.test import TestCase
from rest_framework.test import APIRequestFactory
from todo.models import User, UserProfile
from rest_framework.test import force_authenticate


# Create your tests here.

class TestUpdatUser(TestCase):
    def setUp(self): 
        User.objects.create_user(username="TestPerson",email="testperson@gmail.com", password= "password1")
    def testchangeemail(self):
        factory = APIRequestFactory
        user = User.objects.get(username='TestPerson') 
        request = factory.put(path='/user/settings/',data={'username': 'testperson2@gmail.com'}, format='json')   
    def testchangepassword(self): 
     /*   factory = APIRequestFactory
        user = User.objects.get(username='TestPerson')
        request = factory.put('/user/settings/',{'title': 'new idea'}, format='json')
        force_authenticate(request, user=user)*/
    

