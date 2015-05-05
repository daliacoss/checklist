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

	# tasks = db.session.query(models.Task).order_by(models.Task.id).all()
	# todayTasks = []
	# toPop = set()
	# children = {}

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

	# 	if task.has_parent():
	# 		if not children.get(task.parent_task_id):
	# 			children[task.parent_task_id] = [task]
	# 		else:
	# 			children[task.parent_task_id].append(task)

	# 		#popping the task means that it will inherit today/later status from its parent
	# 		toPop = toPop.union(set([i]))

	# for i, task in enumerate(tasks):
	# 	if hasattr(task, "hidden") and task.hidden:
	# 		continue

	# 	#if task has children, add children to task object
	# 	if task.id in children:
	# 		task.children = children[task.id]
	# 	if task.is_today and not task.has_parent():
	# 		todayTasks.append(task)
	# 		#if task has a parent, it was already added to toPop
	# 		toPop = toPop.union(set([i]))

	# pop(tasks, *toPop)
	# # print [task.view_id for task in todayTasks]
	# # print [task.view_id for task in tasks]
	# # it is possible to sort each list even if view_id is None
	# [l.sort(key = lambda t: t.view_id) for l in [tasks, todayTasks]]
	# todayTasks[0].updateViewID(0)

	# print toPop
	# print todayTasks
	# print tasks

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

	# def sortRecursively(collection, keyFunc, attr, attrFunc):
	# 	collection.sort(key=key)
	# 	for item in collection:
	# 		if 

	# for taskViews in [todayTaskViews, laterTaskViews]:
	# 	tasks = [models.Task.query.filter_by(id=t.task_id).one() for t in taskViews]
	# 	taskTable = {}
	# 	for task in tasks:
	# 		taskTable[task.id] = task

	# 	#associate children with parents
	# 	for task in tasks:
	# 		if task.has_parent():
	# 			#TODO: account for orphaned tasks
	# 			parent = taskTable[task.parent_task_id]
	# 			if not parent.__dict__.get("children"):
	# 				parent.children = [task]
	# 			else:
	# 				parent.children.append(task)

	# 	#clear list
	# 	[tasks.pop(0) for i in range(len(tasks))]

	# 	#ensure only the top ancestors are in the list
	# 	for k,v in taskTable.items():
	# 		if not v.has_parent():
	# 			tasks.append(v)

	# 	taskColumns.append(sorted(tasks, key = lambda t: models.TaskView.query.filter_by(task_id=t.id).one()))

	print [(t.name, t.children) for t in todayTaskViews]
	return render_template('index.html', todayTasks=todayTaskViews, laterTasks=laterTaskViews)
