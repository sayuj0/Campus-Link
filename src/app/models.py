from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    """
    User model for authentication and login.
    
    Stores user account information including credentials.
    Inherits from UserMixin to work with Flask-Login.
    
    Attributes:
        id (str): Unique user identifier (primary key)
        name (str): User's display name
        about (str): Optional user description
        passwd (bytes): Encrypted password hash
    """
    __tablename__ = 'users'
    id: str = db.Column(db.String, primary_key=True)
    name: str = db.Column(db.String)
    about: str = db.Column(db.String)
    passwd: bytes = db.Column(db.LargeBinary)

class School(db.Model):
    """
    School model representing educational institutions.
    
    Stores basic school information including location and status.
    Used as endpoints for transportation cost calculations.
    
    Attributes:
        id (int): Unique school identifier (primary key)
        name (str): School name (required)
        address (str): School physical address
        _type (str): School type (elementary/middle/high school) (required)
        status (str): Current operational status (Open/Closed) (required)
    """
    __tablename__ = 'schools'
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String, nullable=False)
    address: str = db.Column(db.String)
    _type: str = db.Column(db.String, nullable=False)
    status: str = db.Column(db.String, nullable=False)

    def __str__(self) -> str:
        """
        String representation of the School object.
        
        Returns:
            str: Formatted string showing school ID and name
        """
        return f'<School(id={self.id}, name={self.name})>'

class TransportationCost(db.Model):
    """
    Transportation cost model for routes between schools.
    
    Represents the cost of transportation from one school to another.
    Uses composite primary key of from_school_id and to_school_id.
    
    Attributes:
        from_school_id (int): Source school ID (foreign key, primary key)
        to_school_id (int): Destination school ID (foreign key, primary key)
        cost (int): Transportation cost between schools (required)
        from_school (School): Relationship to source school
        to_school (School): Relationship to destination school
    """
    __tablename__ = 'transportation_costs'
    from_school_id: int = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False, primary_key=True)
    to_school_id: int = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False, primary_key=True)
    cost: int = db.Column(db.Integer, nullable=False)
    from_school = db.relationship("School", foreign_keys=[from_school_id])
    to_school = db.relationship("School", foreign_keys=[to_school_id])

    def __str__(self) -> str:
        """
        String representation of the TransportationCost object.
        
        Returns:
            str: Formatted string showing from/to schools and cost
        """
        return f'<Cost(from_school={self.from_school}, to_school={self.to_school}, cost={self.cost})>'