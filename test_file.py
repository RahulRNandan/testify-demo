from testify import TestCase, setup, teardown, assert_equal

class FileProcessorTest(TestCase):
    @setup
    def create_file(self):
        self.file=open("temp_test.txt", "w")
    @teardown
    def remove_file(self):
        self.file.close()
    def test_write(self):
        self.file.write("hello")
        assert_equal(self.file.closed, False)