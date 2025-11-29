i fill we have to make something that trigger this condition and move them properly , something like which calls when user routine is ends(basically it refreshed the after day tasks via call the utilities or functions), or no need of that , i mean they will manage separately to trigger and call the function for movement, tell me what you think , give me a best suggesion which most of big comanies do to handle this kind of stuff.

first review my above suggesion and tell me the best way because the below changes are based on the routine ends system.ones we established that ,  then we make this following changes in tasks page:
--------------------------------------------------------------------
✅ 1. Auto-Move Logic for (Upcoming tasks→ Today’s tasks)

Add a single utility function:moveUpcomingTasksToToday()Do not duplicate this logic anywhere else.

The function must:
	1.	Read all tasks with status = “upcoming”
	2.	For each task:
	•	If task date == today date AND
	•	Yesterday’s last routine has finished(check if routines is ended  then only move)          Before moving tasks:
	                    •	Check the last routine block for yesterday
                      •	If last block end time is in the future, do NOT move tasks yet
	    •	Only move when:             now > yesterday_last_routine_end→ move the task into Today by updating its status 
	3.	Never create duplicates
	4.	Never move tasks with status “done”

Call this function:• I think u should call this on day routine is ended so even user is still on app it works on realtime
	    •	On backend startup
 	    •  On each user login
	    •  On app open/refresh
(whichever is simplest in our existing structure)

✅  Aftertasks moving from upcoming to today:After tasks moved, if tasks total durations are greater than the ’work block’ duration , then it should show red text warning(message: tasks durations are more then your work routine ,plz manage your WORK BLOCK timings) at the right after the main “TASK TITLE”,this condition should check when the upcoming tasks move  to todays box


✅ 2. In todays plan:Implement full logic + UI behaviors for handling unchecked tasks when a daily routine ends, and how these tasks appear on tasks page :if the todays routine is ended (routine),and user don’t checked(via checkbox) the tasks and the routine is ended it should move them to unfinished box and change their status=unfinished, also on ui in unfinished box the tasks should be read only same as we show in “Done tasks ” box


When the last routine of the day finishes:

For every task with:
status == "today"
checkbox == unchecked

Do this: status = "unfinished"

Also:
	•	Remove them from Today’s box
	•	Do NOT move them to Done
	•	Do NOT return them to Upcoming
	•	Push them into the Unfinished section


    Unfinished Section Requirements

UI Behavior:same as we show tasks in the "Done" section
- Show a subtle red/amber border
- Title slightly dimmed (not extremely dull, but clearly not active)