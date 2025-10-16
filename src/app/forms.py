from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, InputRequired, Length

class SignUpForm(FlaskForm):
    """
    Form for new users to create an account.
    
    This form collects basic user information like ID, name, and password.
    The password must be at least 8 characters long for security.
    """
    id = StringField('Id', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    about = TextAreaField('About')
    # Added length validator to ensure password is at least 8 characters long (10/02/2025 AG)
    passwd = PasswordField('Password', validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters.')])
    passwd_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class LoginForm(FlaskForm):
    """
    Simple login form for existing users.
    
    Users enter their ID and password to access the system.
    """
    id = StringField('Id', validators=[DataRequired()])
    passwd = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class SchoolCreateForm(FlaskForm):
    """
    Form to add a new school to the system.
    
    Collects school name, address, type (elementary/middle/high), and status (open/closed).
    All fields are required except address.
    """
    # id = IntegerField('Id', validators=[InputRequired()])
    name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address')
    type = SelectField('Type', choices=['elementary school', 'middle school', 'high school'], validators=[DataRequired()])
    status = SelectField('Status', choices=['Open', 'Closed'])
    submit = SubmitField('Confirm')

class SchoolUpdateForm(FlaskForm):
    """
    Form to edit an existing school's information.
    
    Similar to create form but used when updating school details.
    Pre-fills with current school data.
    """
    # id = IntegerField('Id', render_kw = {'disabled': 'disabled'})
    name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address')
    type = SelectField('Type', choices=['elementary', 'middle', 'high school'], validators=[DataRequired()])
    status = SelectField('Status', choices=['Open', 'Closed'])
    submit = SubmitField('Confirm')

class SchoolDeleteForm(FlaskForm):
    """
    Form that shows school info before deleting it.
    
    All fields are disabled (read-only) so user can see what they're deleting.
    Only the submit button is clickable.
    """
    # id = IntegerField('Id', render_kw = {'disabled': 'disabled'})
    name = StringField('Name', render_kw = {'disabled': 'disabled'})
    address = StringField('Address', render_kw = {'disabled': 'disabled'})
    type = SelectField('Type', choices=['elementary', 'middle', 'high school'], render_kw = {'disabled': 'disabled'})
    status = SelectField('Status', choices=['Open', 'Closed'], render_kw = {'disabled': 'disabled'})
    submit = SubmitField('Confirm')

class TransportationCostForm(FlaskForm):
    """
    Form to add transportation costs between schools.
    
    Shows which school you're starting from (disabled field).
    User enters destination school and the cost to get there.
    """
    from_school_id = SelectField('From School', coerce=int, choices=[])  # Changed from IntegerField to SelectField
    to_school = SelectField('To School', coerce=int, choices=[])  # Changed from StringField to SelectField  
    cost = IntegerField('Cost', validators=[DataRequired()])
    submit = SubmitField('Confirm')


class OptimizationForm(FlaskForm):
    """
    Form to find the best route between schools.
    
    User picks a destination school and the system calculates 
    the cheapest route using the transportation costs.
    """
    target_school_id = SelectField(
        'Destination School', 
        coerce=int, 
        choices=[],              # filled in view
        validators=[DataRequired(message='Select a destination')]
    )
    submit = SubmitField('Find Optimal Path')