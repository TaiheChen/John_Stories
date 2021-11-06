import datetime

import matplotlib.pyplot as plt


# generate x axis according to recent 10 days
def get_x_axis():
    today = datetime.date.today()
    begin = datetime.date(2021, 1, 1)
    delta = datetime.timedelta(days=1)
    temp = []
    while begin <= today:
        temp.append(begin.strftime("%m%d"))
        begin += delta
    x_axis_str = temp[(len(temp) - 10):]
    x_axis_int = []
    for ele in x_axis_str:
        x_axis_int.append(int(ele))

    return x_axis_str, x_axis_int


# draw chart, save to file
def generate_chart(x_axis_str, y_axis1, y_axis2):
    # set x axis and y axis for two lines
    plt.plot(x_axis_str, y_axis1, '.-', label='Views for recent 10 days')
    plt.plot(x_axis_str, y_axis2, '.-', label='Downloads for recent 10 days')
    # set the current tick locations and labels of the x-axis.
    plt.xticks(x_axis_str)
    plt.xlabel('Month and Date')
    # draw two lines in the chart
    plt.legend()
    # save the chart to save_path
    save_path = './static/' + get_chart_name() + '.jpg'
    # another path without static for HTML file
    path = get_chart_name() + '.jpg'
    plt.savefig(save_path)
    # clear buffer in plt
    plt.cla()
    plt.clf()
    plt.close("all")
    return path


# define the chart's name according to the current time
def get_chart_name():
    now = datetime.datetime.now()
    name = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second)
    return name
