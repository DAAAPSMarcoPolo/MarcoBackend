import pickle

class Test:
    def __init__(self):
        self.name = "Testing"


test = Test()
output = open('data.pkl', 'wb')
pickle.dump(test, output)
output.close()

pkl_file = open('data.pkl', 'rb')
test1 = pickle.load(pkl_file)
pkl_file.close()
test1.name = 'dan'
print(test1.name)
print(test.name)

