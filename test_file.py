from testify import TestCase, setup, teardown, assert_equal, suite

class FileProcessorTest(TestCase):
    @setup
    def suites(self, test_method=None): 
        return {'fast', 'unit'}
    def create_file(self):
        self.file=open("temp_test.txt", "w")
    @teardown
    def remove_file(self):
        self.file.close()
    def test_write(self):
        self.file.write("hello")
        assert_equal(self.file.closed, False)