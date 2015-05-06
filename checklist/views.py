from checklist import app, db, models, resources
from flask import request, render_template, url_for
from datetime import datetime

HOURS_UNTIL_HIDDEN = 10

def pop(l, *indices):
	popped = 0
	for i, index in enumerate(indices):
		l.pop(index-popped)
		popped += 1

# @app.route("/update", methods=["POST", "PUT"])
# def update():
# 	print request.form
# 	return "hi\n"

def sortTaskViewDescendants(taskViews):
	"""assumes taskViews is already sorted"""

	for view in taskViews:
		view.children = models.TaskView.query\
			.filter_by(task_column=view.task_column, parent_view_id=view.id)\
			.order_by(models.TaskView.view_index)\
			.all()
		sortTaskViewDescendants(view.children)

def taskViewsToTasks(taskViews):

	for i, view in enumerate(taskViews):
		if view.__dict__.get("children"):
			taskViewsToTasks(view.children)
			children = view.children
		else:
			children = []
		taskViews[i] = models.Task.query.filter_by(id=view.task_id).one()
		taskViews[i].children = children

@app.route("/")
def index():

	# for i, task in enumerate(tasks):
	# 	if task.datetime_completed:
	# 		#if task was completed a while ago, don't show it
	# 		delta = (datetime.utcnow() - task.datetime_completed).total_seconds()
	# 		# print task.name, delta / 3600.
	# 		if delta / 3600. >= HOURS_UNTIL_HIDDEN:
	# 			toPop = toPop.union(set([i]))
	# 			task.hidden = True
	# 			#we skip to the next iteration b/c we're erasing the task from view anyway
	# 			continue

	todayTaskViews, laterTaskViews = [
		models.TaskView.query\
			.filter_by(task_column=i, parent_view_id=None)\
			.order_by(models.TaskView.view_index)\
			.all()
		for i in range(2)
	]
	# laterTaskViews = models.TaskView.query.filter_by(task_column=1).order_by(models.TaskView.view_index).all()

	sortTaskViewDescendants(todayTaskViews)
	sortTaskViewDescendants(laterTaskViews)
	taskColumns = []

	taskViewsToTasks(todayTaskViews)
	taskViewsToTasks(laterTaskViews)

	# print [(t.name, t.children) for t in todayTaskViews]
	return render_template('index.html', todayTasks=todayTaskViews, laterTasks=laterTaskViews)
