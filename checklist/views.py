from checklist import app, db, models
from flask import request, render_template, url_for

@app.route("/")
def index():

	tasks = db.session.query(models.Task).all()
	todayTasks = []
	toPop = []

	for i, task in enumerate(tasks):
		if task.is_today:
			todayTasks.append(task)
			toPop.append(i)

	for i in toPop:
		tasks.pop(i)

	return render_template('index.html', todayTasks=todayTasks, laterTasks=tasks)
