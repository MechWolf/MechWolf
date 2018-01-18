import plotly as py
import plotly.figure_factory as ff
import datetime

df = [dict(Task="Job A", Start='2000-01-01 0:00:00', Finish='2000-01-01 0:15:00'),
      dict(Task="Job B", Start='2000-01-01 0:00:00', Finish='2000-01-01 0:19:00'),
      dict(Task="Job C", Start='2000-01-01 0:00:00', Finish='2000-01-01 0:10:00')]

fig = ff.create_gantt(df)
py.offline.plot(fig, filename='gantt-simple-gantt-chart')