from app.extensions import db

user_stores = db.Table('user_stores',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('store_id', db.Integer, db.ForeignKey('stores.id'), primary_key=True),
    db.Column('created_at', db.DateTime, nullable=False, default=db.func.current_timestamp())
) 