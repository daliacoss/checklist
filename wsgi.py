import sys, os

sys.path.insert(0, os.path.split(os.path.abspath(__file__))[0])
from checklist import app as application

if __name__ == "__main__":
	application.run(debug=True)
