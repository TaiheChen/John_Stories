import datetime
import os

from flask import Flask, render_template, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy

from forms import EditStoryForm
from txt2png import generateImg
from chart import get_x_axis, generate_chart

# Create the application object
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///john.db'
db = SQLAlchemy(app)


# Create the table to restore stories
class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    content = db.Column(db.Text, unique=True)


# Create the table to log the user's view actions
class Views(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    storyid = db.Column(db.Integer)
    date = db.Column(db.Integer)


# Create the table to log the user's download actions
class Downloads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    storyid = db.Column(db.Integer)
    date = db.Column(db.Integer)


# Create the database
db.create_all()

# Restore two stories to the database
s1 = Story(title='The Bald Knight', content='''A BALD KNIGHT, who wore a wig, went out to hunt.  A sudden puff 
of wind blew off his hat and wig, at which a loud laugh rang forth from his companions.  He pulled up his horse, 
and with great glee joined in the joke by saying, "What a marvel it is that hairs which are not mine should fly from 
me, when they have forsaken even the man on whose head they grew."''')

s2 = Story(title='The Bear and the Fox', content='''A BEAR boasted very much of his philanthropy, saying that of all
animals he was the most tender in his regard for man, for he had
such respect for him that he would not even touch his dead body. 
A Fox hearing these words said with a smile to the Bear, "Oh!
that you would eat the dead and not the living."  ''')
# Add the stories to the database
db.session.add(s1)
db.session.add(s2)
# Commit the changes to the database
try:
    db.session.commit()
except Exception as e:
    db.session.rollback()
finally:
    db.session.close()


# Create a function to render the home page
@app.route("/")
def homepage():
    # Retrieval the stories from the database
    stories = Story.query.all()
    return render_template("home.html", stories=stories)


# Create a function to render the about page
@app.route("/about")
def about():
    return render_template("about.html")


# Create a function to render the download page
@app.route("/download/<int:story_id>", methods=['GET'])
def download_file(story_id):
    # Insert the download action including storyid and date into the database
    today = datetime.date.today()
    f = today.strftime("%y%m%d")
    new_click = Downloads(storyid=story_id, date=int(f[2:6]))
    db.session.add(new_click)
    # Commit the changes to the database
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(404, description="Downloads database error!")
    finally:
        db.session.close()

    # Get the story's image from the static folder
    path = os.path.join(os.path.dirname(__file__), 'static')
    name = str(story_id) + '.png'
    return send_from_directory(path, name, mimetype='image/png')


# Create a function to render the story's details page
@app.route("/details/<int:story_id>", methods=["POST", "GET"])
def story_details(story_id):
    # Insert the view action including storyid and date into the database
    today = datetime.date.today()
    f = today.strftime("%y%m%d")
    print(int(f[2:6]))
    new_click = Views(storyid=story_id, date=int(f[2:6]))
    db.session.add(new_click)
    # Commit the changes to the database
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(404, description="Views database error!")
    finally:
        db.session.close()

    # Retrieval the story and its views and downloads from the database
    views = Views.query.filter_by(storyid=story_id).count()
    downloads = Downloads.query.filter_by(storyid=story_id).count()
    story = Story.query.get_or_404(story_id)

    # Generate the chart
    # Get the recent 10 days as x axis
    x_axis_str, x_axis_int = get_x_axis()
    # Retrieval the story's views and downloads in recent 10 days as y axis
    y_axis1 = []
    y_axis2 = []
    for day in x_axis_int:
        y_axis1.append(Views.query.filter_by(storyid=story_id, date=day).count())
        y_axis2.append(Downloads.query.filter_by(storyid=story_id, date=day).count())
    # Generate the chart
    src = generate_chart(x_axis_str, y_axis1, y_axis2)
    if story is None:
        abort(404, description="No Story was Found with the given ID")
    # Render the story's details page
    return render_template("details.html", story=story, views=views, downloads=downloads, imgsrc=src)


# Create a function to render the submit stories page
@app.route("/submit", methods=["POST", "GET"])
def submit():
    form = EditStoryForm()
    # Check if the form is submitted
    if form.validate_on_submit():
        # Retrieval the submitted story's title and content from the form
        new_story = Story(title=form.title.data, content=form.content.data)
        # Add the story to the database
        db.session.add(new_story)
        # Commit the changes to the database
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return render_template("submit.html", form=form, message="This Story already exists in the system!")
        finally:
            db.session.close()
        # Merge the submitted story's title and content into the whole content
        whole_story = form.title.data + '\n' + form.content.data
        # Generate the image named as the story's id and save it in the static folder
        story_index = str(Story.query.count())
        generateImg(whole_story, './static/' + story_index + '.png')
        # Render the submit stories page with a successful message
        return render_template("submit.html", message="Successfully submit a new story!")
    # Render the initial submit stories page
    return render_template("submit.html", form=form)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
