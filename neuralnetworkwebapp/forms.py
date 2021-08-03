from flask_wtf import FlaskForm
from wtforms import SelectField

class DatasetSelectionForm(FlaskForm):
    dataset = SelectField("Choose Dataset",
                          validators=[DataRequired()],
                          choices=['SciKit-Learn Moons',
                                   'Pima Indians Diabetes'])
