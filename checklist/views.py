from checklist import app, db, models, resources
from flask import request, render_template, url_for
from datetime import datetime

HOURS_UNTIL_HIDDEN = 20

def pop(l, *indices):
	popped = 0
	for i, index in enumerate(indices):
		l.pop(index-popped)
		popped += 1

# @app.route("/update", methods=["POST", "PUT"])
# def update():
# 	print request.form
# 	return "hi\n"

@app.route("/")
def index():

	tasks = db.session.query(models.Task).order_by(models.Task.id).all()
	todayTasks = []
	toPop = set()
	children = {}

	for i, task in enumerate(tasks):
		if task.datetime_completed:
			#if task was completed a while ago, don't show it
			delta = (datetime.utcnow() - task.datetime_completed).total_seconds()
			if delta / 3600. >= HOURS_UNTIL_HIDDEN:
				toPop = toPop.union(set([i]))
				task.hidden = True
				#we skip to the next iteration b/c we're erasing the task from view anyway
				continue

		if task.has_parent():
			if not children.get(task.parent_task_id):
				children[task.parent_task_id] = [task]
			else:
				children[task.parent_task_id].append(task)

			#popping the task means that it will inherit today/later status from its parent
			toPop = toPop.union(set([i]))

	for i, task in enumerate(tasks):
		if hasattr(task, "hidden") and task.hidden:
			continue

		#if task has children, add children to task object
		if task.id in children:
			task.children = children[task.id]
		if task.is_today and not task.has_parent():
			todayTasks.append(task)
			#if task has a parent, it was already added to toPop
			toPop = toPop.union(set([i]))

	pop(tasks, *toPop)
	# print toPop
	# print todayTasks
	# print tasks

	return render_template('index.html', todayTasks=todayTasks, laterTasks=tasks)
