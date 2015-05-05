$.fn.ignoreChildren = function(sel){
  return this.clone().children(sel).remove().end();
};

$(document).ready(function(){

	var editButton = $(".task_column .li_edit");
	var newTaskButton = $("#task_new_button");
	var moveButton = $(".task_column .li_move");

	var liContainer = $(".li_container");

	setLiContainerEvents(liContainer);
	setEditButtonEvents(editButton);
	setMoveButtonEvents(moveButton);

	newTaskButton.click(function(){
		if (! $(this).data("open")){
			openTaskCreator($(this));
		}
		else {
			closeTaskCreator($(this), $(this).parent());
		}
	})
});

function setLiContainerEvents(liContainer){
	liContainer.mouseenter(function() {

		var editButton = $(this).parent().children(".li_edit");
		if (editButton.data("open") || editButton.data("subtaskOpen")){
			return;
		}

		var el = $(this).find(".li_marker");
		var li = $(this).find("li");

		if ($(this).hasClass("checked")){
			el.text("–");
		}
		else {
			el.text("✔")
		}
	});

	liContainer.mouseleave(function() {

		var editButton = $(this).parent().children(".li_edit");
		if (editButton.data("open") || editButton.data("subtaskOpen")){
			return;
		}

		var el = $(this).find(".li_marker");
		var li = $(this).find("li");
		if ($(this).hasClass("checked")){
			el.text("✔");
		}
		else {
			el.text("–");
		}
	});

	liContainer.click(function() {

		//if editor is open or any buttons exist
		var id = $(this).parent().data("task_id");
		var isToday = ! $(this).closest(".task_column").is("#right");
		var editButton = $(this).parent().children(".li_edit");
		if (editButton.data("open") || editButton.data("subtaskOpen") || $(this).find("input").length){
			return;
		}

		var el = $(this).find(".li_marker");
		var checked = $(this).hasClass("checked")
		// var li = $(this).find("li");
		if (checked){
			$(this).removeClass("checked");
			el.text("–");

			toggleTaskCompleteInDB(id, false, isToday);
		}
		else{
			$(this).addClass("checked");
			el.text("✔");

			//mark descendants as checked
			$.each(getTaskDescendants($(this).parent()), function(i, task){
				// console.log(i);
				var c = $(".li_container", task);
				if (! c.hasClass("checked")){
					c.addClass("checked");
				}
			});

			toggleTaskCompleteInDB(id, true, isToday);
		}
	});
}

function setEditButtonEvents(editButton){
	editButton.ready(function() {
		$(this).data("open", false);
	});

	editButton.click(function() {
		if (! $(this).data("open")){
			openEditor($(this));
		}
		else {
			closeEditor($(this));
		}
	});
}

function setMoveButtonEvents(moveButton){
	moveButton.click(function () {
		var up = ! $(this).hasClass("down");
		var task = $(this).parent();
		moveTaskWithinColumn(task, up);
	})
}

function moveTaskWithinColumn(task, up){

	var descendants = getTaskDescendants(task);
	var siblingFunction, insertFunction;

	if (up){
		siblingFunction = "prev";
		insertFunction = "before";
	}
	else {
		siblingFunction = "next";
		insertFunction = "after";
	}

	var sibling = task[siblingFunction]();
	while (sibling.data("depth") != undefined && sibling.data("depth") != task.data("depth")){
		sibling = sibling[siblingFunction]();
	}

	if (! sibling.length){
		return;
	}

	task.detach();
	$.each(descendants, function(i, d){
		d.detach();
	})

	//if moving down, insert task after last sibling descendant
	var siblingDescendants = getTaskDescendants(sibling);
	if (insertFunction == "after" && siblingDescendants.length){
		siblingDescendants[siblingDescendants.length-1][insertFunction](task);
	}
	else {
		sibling[insertFunction](task);
	}

	$.each(descendants, function(i, d){
		if (insertFunction == "before"){
			sibling[insertFunction](d);
		}
		// else if (siblingDescendants.length){
		// 	siblingDescendants[siblingDescendants.length-1][insertFunction](d);
		// }
		else {
			task[insertFunction](d);
		}
	})

	updateTaskViewInDB(task.data("task_id"), (up) ? -1 : 1, ! task.closest(".task_column").is("#right"));
	// }
	// else {
	// 	var next = task.next();
	// 	while (next.data("depth") != undefined && next.data("depth") != task.data("depth")){
	// 		next = next.next();
	// 	}
	// 	console.log(next.length);
	// 	// if (next.length){
	// 	// 	task.detach();
	// 	// 	$.each(descendants, function(i, d){
	// 	// 		d.detach();
	// 	// 	})
	// 	// 	next.after(task);
	// 	// 	$.each(descendants, function(i, d){
	// 	// 		next.after(d);
	// 	// 	})
	// 	// }
	// }
}

function openEditor(editButton){

	var container = editButton.parent();
	var li = container.find("li");
	var isToday = ! container.closest(".task_column").is("#right");

	// getTaskDescendants(container);

	//change cursor
	li.parent().css("cursor", "auto");

	//capture task name and comment
	var taskName = li.children(".task_name").text().trim();
	var taskComment = li.children(".task_comment").text().trim();

	editButton.data("open", true);
	editButton.data("taskName", taskName);
	editButton.data("taskComment", taskComment);

	li.children(".task_name").html("<textarea class=\"task_name_editor\">" + taskName + "</textarea>");
	li.children(".task_comment").html("<textarea class=\"task_comment_editor\">" + taskComment + "</textarea>");

	var buttons = [];
	var labels = ["OK", "Cancel", "Move to Later", "Add Subtask", "Delete"];
	if (container.parent().parent().is("#right")){
		labels[2] = "Move to Today";
	}
	$.each(labels, function(index, value){
		var b = $("<input>", {
			"type": "button",
			"class": "task_editor_button",
			"value": value
		});
		buttons.push(b);
		li.append(b);
	});

	buttons[0].click(function() {

		taskName = li.find(".task_name_editor").val();
		taskComment = li.find(".task_comment_editor").val();

		editButton.data("taskName", taskName);
		editButton.data("taskComment", taskComment);

		// console.log(taskName);
		editTaskInDB(container.data("task_id"), taskName, taskComment, isToday);

		closeEditor(editButton);
	});

	buttons[1].click(function () {
		closeEditor(editButton);
	});

	buttons[2].click(function () {
		moveTask(container);
	});

	buttons[3].click(function () {
		closeEditor(editButton);
		openTaskCreator($(this), container);
	});

	buttons[4].click(function () {
		deleteTask(container);
	});
}

function closeEditor(editButton){

	var taskName = editButton.data("taskName");
	var taskComment = editButton.data("taskComment");

	var container = editButton.parent();
	var li = container.find("li");

	li.children(".task_name").html(taskName);
	li.children(".task_comment").html(taskComment);

	$("input", li).remove();

	//delay close/open switch by 10 ms to allow container onclick to finish
	setTimeout(function() {
		editButton.data("open", false);
	}, 10);

	//reset cursor
	li.parent().css("cursor", "pointer");
}

function openTaskCreator(newTaskButton, taskParent){

	newTaskButton.data("open", true);

	var container;
	if (! taskParent){
		container = newTaskButton.parent();
		container.css("text-align", "inherit");
	}
	else {
		// container = taskParent.clone();
		container = taskParent.children(".li_container");
		$(".li_edit", container.parent()).data("subtaskOpen", true);
		container.css("cursor", "auto");
	}

	//we detach before the .html call so the element still exists
	newTaskButton.detach();

	if (! taskParent){
		container.html("");
	}
	else{
		var indent = parseInt(taskParent.children(".li_edit").get(0).style.marginLeft || 0) + 1;
		container.append($("<span/>", {"class":"li_marker"})
			.css("margin-left", indent.toString() + "em")
			.text("–"));
	}

	container
		.append($("<div/>")
			.append($("<textarea/>", {"class":"task_name_editor"}).text("new task"))
			.append($("<br/>"))
			.append($("<textarea/>", {"class":"task_comment_editor"})));
	if (taskParent){
		// $("textarea", container).css("width: 0%");
		$("div", container).css("margin-left", "5em");
		// $("textarea", container).css("width: 100%");
	}

	var buttons = [];
	$.each(["OK", "Cancel"], function(index, value){
		var b = $("<input>", {
			"type": "button",
			"class": "task_editor_button",
			"value": value
		});
		buttons.push(b);
		$("div", container).append(b);
	});
	
	buttons[0].click(function() {

		taskName = container.find(".task_name_editor").val();
		taskComment = container.find(".task_comment_editor").val();

		if (! taskParent){
			addTask(container.parent().find("ul"), taskName, taskComment);
		}
		else{
			addTask(container.parent().parent(), taskName, taskComment, taskParent);
		}
		closeTaskCreator(newTaskButton, container, taskParent);
	})

	buttons[1].click(function() {
		closeTaskCreator(newTaskButton, container, taskParent);
	})
}

function closeTaskCreator(newTaskButton, container, taskParent){

	if (! taskParent){
		container.css("text-align", "center");
		container.html("");
		container.append(newTaskButton);
		newTaskButton.data("open", false);		
	}
	else {
		$("div", container).remove();
		$(".li_marker", container).last().remove();
		setTimeout(function(){
			$(".li_edit", container.parent()).data("subtaskOpen", false);
		}, 10);
		container.css("cursor", "pointer");
	}
}

function getTaskDescendants(task){
	var depth = parseInt(task.data("depth"));
	var descendants = []

	task.nextAll().each(function(i){
		if ($(this).data("depth") <= depth){
			return false;
		}
		descendants.push($(this));
	})

	return descendants;
}

function createTask(taskName, taskComment){
	var taskPrototype = $("<div/>")
		.append($("<span/>", {"class":"li_edit"}).text("#"))
		.append($("<span/>", {"class":"li_move"}).html("<span>▲</span>"))
		.append($("<span/>", {"class":"li_move down"}).html("<span>▼</span>"))
		.append($("<div/>", {"class":"li_container"})
			.append($("<span/>", {"class":"li_marker"}).text("–"))
			.append($("<li/>")
				.append($("<span/>", {"class":"task_name"}).text(taskName))
				.append("<br/>")
				.append($("<span/>", {"class":"task_comment"}).text(taskComment))));

	setLiContainerEvents(taskPrototype.children("div"));
	setEditButtonEvents(taskPrototype.children(".li_edit"));
	setMoveButtonEvents(taskPrototype.children(".li_move"))

	return taskPrototype;
}

function addTask(listElement, taskName, taskComment, parent){

	var newItem = createTask(taskName, taskComment);
	var newItemEditButton = newItem.find(".li_edit");

	//right column is "later"; left column is "today"
	var isToday = (listElement.closest(".task_column")[0].id == "right") ? false : true;
	addTaskToDB(taskName, taskComment, isToday, (parent) ? parent.data("task_id"): null, newItem);

	newItemEditButton.data("open", false);
	if (parent){
		newItem.data("depth", parseInt(parent.data("depth")) + 1);
	}
	else {
		newItem.data("depth", 0);
	}

	if (parent){
		var indent = parseInt(parent.find(".li_container").get(0).style.marginLeft || 0) + 1;
		$.each([".li_container", ".li_edit", ".li_marker", ".li_move"], function(index, selector){
			// $(".li_container", newItem).css("margin-left", indent.toString() + "em");
			$(selector, newItem).css("margin-left", indent.toString() + "em");
		});
		parent.after(newItem);
	}
	else{
		listElement.append(newItem);
	}
}

function deleteTask(task){

	$.each(getTaskDescendants(task), function(i, subtask){
		// console.log(i, subtask);
		subtask.remove();
	});
	var id = task.data("task_id");
	var isToday = ! task.closest("task_column").is("#right");
	task.remove();
	deleteTaskFromDB(id, isToday);
}

function moveTask(task){

	var destination = $("ul", task.parent().parent().siblings());
	var isToday = ! task.parent().parent().siblings().is("#right")
	var descendants = getTaskDescendants(task);

	destination.append(task.detach());
	closeEditor($(".li_edit", task));

	$.each(descendants, function(i, subtask){
		// console.log(i, subtask);
		destination.append(subtask.detach());
	})
	// console.log(destination);

	editTaskInDB(task.data("task_id"), null, null, isToday);
}

function displayStatusMessage(message, isToday, timeout){

	var serverStatusSpan;
	if (isToday){
		serverStatusSpan = $("#left .task_server_status");
	}
	else {
		serverStatusSpan = $("#right .task_server_status")
	}

	// console.log(serverStatusSpan.text());
	serverStatusSpan.text(message);

	if (timeout != null){
		window.setTimeout(function() {
			serverStatusSpan.text("");
		}, timeout);
	}
}

function addTaskToDB(taskName, taskComment, isToday, parent, taskElement){

	displayStatusMessage("saving...", isToday);
	$.ajax({
		url: "/task",
		type: "PUT",
		data: {name: taskName, comment: taskComment, parent: parent, is_today: isToday},
		dataType: "json",
		success: function (result) {
			if (result["msg"] == "success"){
				taskElement.data("task_id", result["data"]["task"]["id"]);
				displayStatusMessage("saved", isToday, 1000);
				// console.log($("#left .task_server_status"))
			}
		},
		error: function (jqXHR, textStatus, errorThrown) {
			displayStatusMessage(errorThrown, isToday, 1000);
		}
	});
}

function deleteTaskFromDB(taskID, isToday){

	displayStatusMessage("saving...", isToday);
	$.ajax({
		url: "/task",
		type: "DELETE",
		data: {id: taskID},
		dataType: "json",
		success: function (result) {
			if (result["msg"] == "success"){
				displayStatusMessage("saved", isToday, 1000);
			}
		},
		error: function (jqXHR, textStatus, errorThrown) {
			displayStatusMessage(errorThrown, isToday, 1000);
		}
	});
}

function updateTaskViewInDB(taskID, delta, isToday){
	displayStatusMessage("saving...", isToday);
	$.ajax({
		url: "/task",
		type: "POST",
		data: {id: taskID, view_index_delta: delta},
		dataType: "json",
		success: function (result) {
			if (result["msg"] == "success"){
				displayStatusMessage("saved", isToday, 1000);
			}
		},
		error: function (jqXHR, textStatus, errorThrown) {
			displayStatusMessage(errorThrown, isToday, 1000);
		}
	});
}

function editTaskInDB(taskID, taskName, taskComment, isToday, parent){
	
	var data = {id: taskID}
	if (taskName != null) data["name"] = taskName;
	if (taskComment != null) data["comment"] = taskComment;
	if (isToday != null) data["is_today"] = isToday;
	// console.log(taskName, parent);
	if (parent != null) data["parent"] = parent;

	displayStatusMessage("saving...", isToday);
	$.ajax({
		url: "/task",
		type: "POST",
		data: data,
		dataType: "json",
		success: function (result) {
			if (result["msg"] == "success"){
				displayStatusMessage("saved", isToday, 1000);
			}
		},
		error: function (jqXHR, textStatus, errorThrown) {
			displayStatusMessage(errorThrown, isToday, 1000);
		}
	});
}

function toggleTaskCompleteInDB(taskID, complete, isToday){
	$.ajax({
		url: "/task",
		type: "POST",
		data: {id: taskID, checked: complete},
		dataType: "json",
		success: function (result) {
			if (result["msg"] == "success"){
				displayStatusMessage("saved", isToday, 1000);
			}
		},
		error: function (jqXHR, textStatus, errorThrown) {
			displayStatusMessage(errorThrown, isToday, 1000);
		}
	});
}

