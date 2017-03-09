from bloghandler import BlogHandler


class MainPage(BlogHandler):

    def get(self):
        self.write('Hello, Udacity!')