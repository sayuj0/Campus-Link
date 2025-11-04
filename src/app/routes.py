from app import app, db, sp
from app.models import User, School, TransportationCost
from app.forms import SignUpForm, LoginForm, SchoolCreateForm, SchoolUpdateForm, SchoolDeleteForm, TransportationCostForm, OptimizationForm
from flask import render_template, redirect, url_for, request, flash, send_from_directory, send_file, Response
from flask_login import login_required, login_user, logout_user
from app.optimizer import ResourceOptimizer
import bcrypt
import sys  # Dijkstra's algorithm implementation using a priority queue
from heapq import heappush, heappop
import tempfile

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index() -> str: 
    """
    Render the main index page.
    
    Returns:
        str: Rendered index.html template
    """
    return render_template('index.html')

# User signup Added 10/02/2025 AG#
@app.route('/users/signup', methods=['GET', 'POST'])
def signup() -> str:
    """
    Handle user registration with form validation and password hashing.
    
    Returns:
        str: Rendered signup template or redirect to login page
    """
    form: SignUpForm = SignUpForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user: User = db.session.query(User).filter_by(id=form.id.data).first()
        if existing_user:
            form.id.errors.append('User ID already exists. Please choose a different ID.')
        # Check that passwords match, if not returns message
        elif form.passwd.data != form.passwd_confirm.data:
            form.passwd_confirm.errors.append('Passwords do not match.')
        # If no errors, create the user
        else:
            # Salt/Hash password
            salt: bytes = bcrypt.gensalt()
            hashed: bytes = bcrypt.hashpw(form.passwd.data.encode('utf-8'), salt)
            user: User = User(
                id=form.id.data,
                name=form.name.data,
                about=form.about.data,
                passwd=hashed
            )
            db.session.add(user)
            db.session.commit()
            # Flash a success message to let user know account was created
            flash('Account created, please log in.')
            # Redirect to login after successful signup
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)

# User login Added 10/02/2025 AG#
@app.route('/users/login', methods=['GET', 'POST'])
def login() -> str:
    """
    Handle user authentication with bcrypt password verification.
    
    Returns:
        str: Rendered login template or redirect to schools list
    """
    form: LoginForm = LoginForm()
    if form.validate_on_submit():
        # Check for user in database
        user: User = db.session.query(User).filter_by(id=form.id.data).first()
        # If user exists and password is correct (checked with bcrypt), log the user in
        if user and bcrypt.checkpw(form.passwd.data.encode('utf-8'), user.passwd):
            login_user(user)
            # Upon successful login, flash success message
            flash('Logged in successfully.')
            # Upon successful login, redirect to the schools list page
            return redirect(url_for('list_schools'))
        # If user doesn't exist or password is incorrect, show error message
        else:
            form.id.errors.append('Invalid user ID or password.')
    return render_template('login.html', form=form)

# User logout Added 10/02/2025 AG#
#To see the logout button, user must be logged in
@login_required
@app.route('/users/signout', methods=['GET', 'POST'])
def signout() -> Response:
    """
    Log out the current user and redirect to login page.
    
    Returns:
        Response: Redirect to login page
    """
    logout_user()
    # Flash a message to let user know they have been signed out
    flash('You have been signed out.')
    # Redirect to login page after logout
    return redirect(url_for('login'))

@app.route('/schools')
@login_required
def list_schools() -> str: 
    """
    Display list of all schools in the system.
    
    Returns:
        str: Rendered schools.html template with schools data
    """
    schools: list[School] = db.session.query(School).all()
    return render_template('schools.html', schools=schools)

@login_required
@app.route('/schools/create', methods=['GET', 'POST'])
def create_school() -> str:
    """
    Handle creation of new schools with form validation.
    
    Returns:
        str: Rendered create template or redirect to schools list
    """
    form: SchoolCreateForm = SchoolCreateForm()
    if form.validate_on_submit():
        school: School = School(
            name=form.name.data,
            address=form.address.data,
            _type=form.type.data,  
            status=form.status.data 
        )
        db.session.add(school)
        db.session.commit()
        return redirect(url_for('list_schools'))
    return render_template('schools/create.html', form=form)

@login_required
@app.route('/schools/<int:id>', methods=['GET', 'POST'])
def update_school(id: int) -> str: 
    """
    Handle updating existing school information.
    
    Args:
        id (int): School ID to update
        
    Returns:
        str: Rendered update template or redirect to schools list
    """
    school: School = School.query.get_or_404(id)
    form: SchoolUpdateForm = SchoolUpdateForm()

    if request.method == 'GET':
        form.process(obj=school)
        form.type.data = school._type

    if form.validate_on_submit():
        school.name = form.name.data
        school.address = form.address.data
        school._type = form.type.data
        school.status = form.status.data
        try:
            db.session.commit()
            flash('School updated successfully.')
            return redirect(url_for('list_schools'))
        except Exception as e:
            db.session.rollback()
            flash('Update failed, please try again.')
            app.logger.error(f'Error updating school {id}: {e}')

    return render_template('schools/update.html', form=form, school=school)

@login_required
@app.route('/schools/<int:id>/delete', methods=['POST', 'GET'])
def delete_school(id: int) -> Response: 
    """
    Handle deletion of a school from the system.
    
    Args:
        id (int): School ID to delete
        
    Returns:
        Response: Redirect to schools list
    """
    school: School = School.query.get_or_404(id)
    try:
        db.session.delete(school)
        db.session.commit()
        flash('School deleted.')
    except Exception as e:
        db.session.rollback()
        flash('Delete failed.')
        app.logger.error(f'Error deleting school {id}: {e}')
    return redirect(url_for('list_schools'))

@login_required
@app.route('/schools/<int:id>/costs', methods=['GET', 'POST'])
def school_costs(id: int) -> str:
    """
    Manage transportation costs from a specific school to other schools.
    
    Args:
        id (int): Source school ID
        
    Returns:
        str: Rendered costs template
    """
    from_school: School = db.session.query(School).get_or_404(id)
    existing_costs: list[TransportationCost] = db.session.query(TransportationCost).filter_by(from_school_id=id).all()
    
    # Get all schools for the dropdown choices
    schools: list[School] = db.session.query(School).all()
    
    # Check if we have at least 2 schools
    if len(schools) < 2:
        flash('You need at least 2 schools to add transportation costs.', 'error')
        return redirect(url_for('list_schools'))
    
    form: TransportationCostForm = TransportationCostForm()
    
    # Set up dropdown choices
    form.from_school_id.choices = [(school.id, school.name) for school in schools]
    form.to_school.choices = [(school.id, school.name) for school in schools if school.id != id]  # Exclude current school
    
    # Set the from_school to current school
    form.from_school_id.data = id
    
    if form.validate_on_submit():
        to_school_id = form.to_school.data
        
        if to_school_id == id:
            flash('Cannot set cost to the same school.')
            return render_template('costs.html', form=form, from_school=from_school, existing_costs=existing_costs, schools=schools)
            
        existing_cost: TransportationCost = db.session.query(TransportationCost).filter_by(from_school_id=id, to_school_id=to_school_id).first()
        if existing_cost:
            existing_cost.cost = form.cost.data
            flash('Transportation cost updated.')
        else:
            db.session.add(TransportationCost(from_school_id=id, to_school_id=to_school_id, cost=form.cost.data))
            flash('Transportation cost added.')
        db.session.commit()
        return redirect(url_for('school_costs', id=id))
        
    return render_template('costs.html', form=form, from_school=from_school, existing_costs=existing_costs, schools=schools)

@app.route('/download/requirements')
def download_requirements() -> Response:
    """
    Download the requirements.txt file from project root.
    
    Returns:
        Response: File download response
    """
    import os
    project_root: str = os.path.abspath(os.path.join(app.root_path, '..', '..'))
    return send_from_directory(project_root, 'requirements.txt', as_attachment=True)

@login_required
@app.route('/schools/<int:id>/routes', methods=['GET', 'POST'])
def school_routes(id: int) -> str: 
    """
    Find optimal routes between schools using Dijkstra's algorithm.
    
    Args:
        id (int): Source school ID
        
    Returns:
        str: Rendered optimizer template with route results
    """
    form: OptimizationForm = OptimizationForm() 
    schools: list[School] = School.query.order_by(School.name).all() 
    form.target_school_id.choices = [(s.id, s.name) for s in schools if s.id != id] 

    if request.method == 'POST' and form.validate_on_submit(): 
        optimizer: ResourceOptimizer = ResourceOptimizer(bidirectional=True)
        result: dict = optimizer.find_optimal_path(id, form.target_school_id.data)
        # Pass target_school_id to template for graph
        return render_template(
            'optimizer.html',
            form=None,
            result=result,
            source_id=id,
            target_id=form.target_school_id.data  # Pass target_id for selected route
        )
    return render_template('optimizer.html', form=form, result=None, source_id=id, target_id=None)

@app.route('/schools/<int:id>/routes/visual', methods=['GET'])
@login_required
def school_routes_visual(id: int) -> Response:
    """
    Generate visual graph showing optimal route between schools.
    Uses pure Python (matplotlib) instead of Graphviz for deployment compatibility.
    
    Args:
        id (int): Source school ID
        
    Returns:
        Response: PNG image file of the route graph
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-GUI backend
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np
        from io import BytesIO
    except ImportError:
        return Response('Visualization requires matplotlib. Please install: pip install matplotlib', 
                       status=500, mimetype='text/plain')
    
    # Query all schools
    schools: list[School] = School.query.order_by(School.id).all()
    school_dict: dict[int, str] = {s.id: s.name for s in schools}
    
    target_id: int = request.args.get('target_id', type=int)
    if not target_id:
        return Response('target_id parameter is required', status=400, mimetype='text/plain')
    
    # Calculate optimal path
    optimizer: ResourceOptimizer = ResourceOptimizer(bidirectional=True)
    result: dict = optimizer.find_optimal_path(id, target_id)
    
    if not result.get('success'):
        return Response(f'Route calculation failed: {result.get("message", "Unknown error")}', 
                       status=400, mimetype='text/plain')
    
    path_ids: list[int] = result['path']
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # Position schools in a circle for better visualization
    num_schools = len(schools)
    angles = np.linspace(0, 2 * np.pi, num_schools, endpoint=False)
    radius = 3
    
    school_positions = {}
    for i, school in enumerate(schools):
        x = radius * np.cos(angles[i])
        y = radius * np.sin(angles[i])
        school_positions[school.id] = (x, y)
    
    # Draw all schools as nodes
    for school in schools:
        x, y = school_positions[school.id]
        if school.id == id:
            color = 'lightgreen'  # Source school
        elif school.id == target_id:
            color = 'lightcoral'  # Target school
        elif school.id in path_ids:
            color = 'yellow'  # Schools in path
        else:
            color = 'lightblue'  # Other schools
            
        circle = plt.Circle((x, y), 0.3, color=color, ec='white', linewidth=2)
        ax.add_patch(circle)
        ax.text(x, y, str(school.id), ha='center', va='center', fontweight='bold', fontsize=10)
        ax.text(x, y-0.6, school.name[:15], ha='center', va='center', fontsize=8, color='white')
    
    # Draw the optimal path
    for i in range(len(path_ids) - 1):
        from_id = path_ids[i]
        to_id = path_ids[i + 1]
        
        x1, y1 = school_positions[from_id]
        x2, y2 = school_positions[to_id]
        
        # Draw arrow
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', color='red', lw=3))
        
        # Add cost label
        cost_obj: TransportationCost = TransportationCost.query.filter_by(
            from_school_id=from_id, to_school_id=to_id).first()
        cost = cost_obj.cost if cost_obj else 0
        
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y, f'${cost}', ha='center', va='center', 
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8),
               fontsize=9, fontweight='bold')
    
    # Set title and formatting
    ax.set_title(f'Optimal Route: {school_dict[id]} → {school_dict[target_id]}\n'
                f'Total Cost: ${result["total_cost"]} | Transfers: {result["num_transfers"]}',
                color='white', fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', 
                  markersize=10, label='Source School'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', 
                  markersize=10, label='Target School'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', 
                  markersize=10, label='Path Schools'),
        plt.Line2D([0], [0], color='red', linewidth=3, label='Optimal Route')
    ]
    ax.legend(handles=legend_elements, loc='upper right', 
             facecolor='black', edgecolor='white', labelcolor='white')
    
    # Save to bytes
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', facecolor='black', 
               bbox_inches='tight', dpi=150)
    img_buffer.seek(0)
    png_bytes = img_buffer.getvalue()
    plt.close()
    
    return Response(png_bytes, mimetype='image/png')
