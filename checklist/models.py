from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func
from checklist import db
import datetime

class Task(db.Model):
	__tablename__ = "tasks"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), index=False, nullable=False)
	comment = db.Column(db.String(300), index=False)
	parent_task_id = db.Column(db.Integer)
	datetime_added = db.Column(db.DateTime(timezone=True))
	datetime_completed = db.Column(db.DateTime(timezone=True), nullable=True)
	is_today = db.Column(db.Boolean, nullable=False)
	view_id = db.Column(db.Integer)

	def __init__(self, name, comment="", is_today=False, **kwargs):
		self.name = name
		self.is_today = is_today
		self.comment = comment
		for k,v in kwargs.items():
			setattr(self, k, v)

		self.children = []
		self.hidden = False

	def has_parent(self):
		return type(self.parent_task_id) == int and self.parent_task_id != self.id

	def collectChildren(self):
		self.children = Task.query.filter_by(parent_task_id=self.id).all()
		return self.children

	def deleteFromSession(self, deleteDescendants=False, deleteView=True):
		"""delete this model from db.session (without committing)"""

		if deleteDescendants:
			for child in self.collectChildren():
				child.deleteFromSession(True)

		if deleteView:
			db.session.delete(TaskView.query.filter_by(task_id=self.id).one())
		db.session.delete(self)

	def markComplete(self, markDescendants=False):

		self.datetime_completed = datetime.datetime.utcnow()
		if markDescendants:
			for child in self.collectChildren():
				child.markComplete(True)

	def createView(self):

		parentID = None
		column = 1
		if self.parent_task_id:
			tmp = db.session.query(TaskView).filter_by(task_id=self.parent_task_id).one()
			parentID = tmp.id
			column = tmp.task_column

		#find the highest view_index of any view with the same parent, and add 1 (parent can be None)
		viewIndex = db.session.query(func.max(TaskView.view_index))\
			.filter_by(parent_view_id=parentID, task_column=column)\
			.one()[0] or -1
		viewIndex += 1

		# print column
		view = TaskView(self.id, viewIndex, parentID, column)

		return view

	def updateView(self, delta, column=None, updateDescendants=False):

		view = TaskView.query.filter_by(task_id=self.id).one()
		if delta:
			view.setViewIndex(view.view_index+delta)

		c = view.task_column
		if column != None and column != c:
			#if column has changed and view has no parent, send to the end of the list
			if not (view.parent_view_id or view.parent_view_id == 0):
				print "changing"
				view.view_index = (db.session.query(func.max(TaskView.view_index))\
					.filter(TaskView.parent_view_id==None)\
					.filter(TaskView.task_column==column)\
					.one()[0] or 0) + 1
			view.task_column = column
		print self.name, ":", view.task_column

		if updateDescendants:
			for child in self.collectChildren():
				print "child", child.name
				child.updateView(0, column, True)
		# if not self.view_id:
		# 	self.view_id = delta
		# else:
		# 	self.view_id += delta

		# siblingsAndSelf = Task.query.filter_by(is_today=self.is_today).order_by(Task.view_id).all()
		# print [x.view_id for x in siblingsAndSelf]
		# for task in siblingsAndSelf:
		# 	print task == self

class TaskView(db.Model):
	__tablename__ = "task_views"

	id = db.Column(db.Integer, primary_key=True)
	task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
	view_index = db.Column(db.Integer, nullable=False)
	parent_view_id = db.Column(db.Integer)
	task_column = db.Column(db.Integer)

	def __init__(self, task_id, view_index=0, parent_view_id=None, task_column=0):
		self.task_id = task_id
		self.view_index = view_index
		self.parent_view_id = parent_view_id
		self.task_column = task_column

	def setViewIndex(self, newIndex):
		endpoints = sorted((self.view_index, newIndex))
		viewsToShift = TaskView.query\
			.filter_by(parent_view_id=self.parent_view_id, task_column=self.task_column)\
			.filter(TaskView.view_index>=endpoints[0])\
			.filter(TaskView.view_index<=endpoints[1])\
			.order_by(TaskView.view_index).all()

		#if view_index is increasing, decrease the indices of the views it jumps in front of
		#else, increase the indices of the views it jumps behind
		direction = cmp(self.view_index, newIndex)
		for view in viewsToShift:
			view.view_index += direction

		self.view_index = newIndex

	def deleteFromSession():

		viewsToShift = TaskView.query\
			.filter_by(parent_view_id=self.parent_view_id, task_column=self.task_column)\
			.filter(TaskView.view_index>self.view_index).all()
		for view in viewsToShift:
			view.view_index += 1

class Milestone(db.Model):
	__tablename__ = "milestones"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), index=False, nullable=False)

	def __init__(self, name):
		self.name = name

class MilestoneTask(db.Model):
	__tablename__ = "milestone_tasks"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), index=False, nullable=False)
	comment = db.Column(db.String(300), index=False)
	parent_task_id = db.Column(db.Integer)
	datetime_added = db.Column(db.DateTime)
	datetime_completed = db.Column(db.DateTime, nullable=True)
	milestone_id = db.Column(db.Integer, db.ForeignKey("milestones.id"), nullable=False)

	def __init__(self, name):
		self.name = name

db.create_all()
