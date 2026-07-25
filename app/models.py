from datetime import datetime
from app import db 

class Estate(db.Model):
    __tablename__ = "estates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    courts = db.relationship("Court", backref="estate")
    checkpoints = db.relationship("Checkpoint", backref="estate")

    def __repr__(self):
        return f"<Estate {self.name}>"


class Court(db.Model):
    __tablename__ = "courts"

    id = db.Column(db.Integer, primary_key=True)
    estate_id = db.Column(db.Integer, db.ForeignKey("estates.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Court {self.name}>"


class Checkpoint(db.Model):
    __tablename__ = "checkpoints"

    id = db.Column(db.Integer, primary_key=True)
    estate_id = db.Column(db.Integer, db.ForeignKey("estates.id"), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey("courts.id"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    court = db.relationship("Court", backref="checkpoints")

    def __repr__(self):
        return f"<Checkpoint {self.name}>"



class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey("checkpoints.id"), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    checkpoint = db.relationship("Checkpoint", backref="staff")

    def __repr__(self):
        return f"<User {self.full_name}>"




class Resident(db.Model):
    __tablename__ = "residents"

    id = db.Column(db.Integer, primary_key=True)# 'parked', 'moved', 'left'i
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255))
    unit_number = db.Column(db.String(50), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey("courts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    court = db.relationship("Court", backref="residents")

    def __repr__(self):
        return f"<Resident {self.full_name} (Unit {self.unit_number})>"


class Visitor(db.Model):
    __tablename__ = "visitors"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    id_number = db.Column(db.String(50))
    host_resident_id = db.Column(db.Integer, db.ForeignKey("residents.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    host_resident = db.relationship("Resident", backref="visitors")

    def __repr__(self):
        return f"<Visitor {self.full_name}>"



class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    color = db.Column(db.String(50))
    vehicle_category = db.Column(db.String(20), nullable=False)
    owner_resident_id = db.Column(db.Integer, db.ForeignKey("residents.id"), nullable=True)
    owner_visitor_id = db.Column(db.Integer, db.ForeignKey("visitors.id"), nullable=True)

    registered_at_checkpoint_id = db.Column(db.Integer, db.ForeignKey("checkpoints.id"), nullable=True)
    registered_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner_resident = db.relationship("Resident", backref="vehicles")
    owner_visitor = db.relationship("Visitor", backref="vehicles")
    registered_at_checkpoint = db.relationship("Checkpoint", backref="vehicles_registered")
    registered_by_user = db.relationship("User", backref="vehicles_registered")

    def __repr__(self):
        return f"<Vehicle {self.plate_number}>"



class CheckpointLog(db.Model):
    __tablename__ = "checkpoint_logs"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey("checkpoints.id"), nullable=False)
    verified_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(255))

    vehicle = db.relationship("Vehicle", backref="checkpoint_logs")
    checkpoint = db.relationship("Checkpoint", backref="logs")
    verified_by_user = db.relationship("User", backref="verified_logs")

    def __repr__(self):
        return f"<CheckpointLog {self.vehicle_id} {self.action}>"



class ParkingSlot(db.Model):
    __tablename__ = "parking_slots"

    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey("courts.id"), nullable=False)
    slot_number = db.Column(db.String(20), nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)

    court = db.relationship("Court", backref="parking_slots")

    def __repr__(self):
        return f"<ParkingSlot {self.slot_number}>"



class ParkingRecord(db.Model):
    __tablename__ = "parking_records"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey("courts.id"), nullable=False)
    parking_slot_id = db.Column(db.Integer, db.ForeignKey("parking_slots.id"), nullable=True)
    location_description = db.Column(db.String(255))
    parked_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(10), default="parked")  r

    vehicle = db.relationship("Vehicle", backref="parking_records")
    court = db.relationship("Court", backref="parking_records")
    parking_slot = db.relationship("ParkingSlot", backref="parking_records")

    def __repr__(self):
        return f"<ParkingRecord {self.vehicle_id} @ court {self.court_id} ({self.status})>"



class BlockingIncident(db.Model):
    __tablename__ = "blocking_incidents"

    id = db.Column(db.Integer, primary_key=True)
    blocking_vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    blocked_vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    blocking_parking_record_id = db.Column(db.Integer, db.ForeignKey("parking_records.id"), nullable=False)
    reported_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(10), default="pending")  

    
    blocking_vehicle = db.relationship(
        "Vehicle", foreign_keys=[blocking_vehicle_id], backref="incidents_caused"
    )
    blocked_vehicle = db.relationship(
        "Vehicle", foreign_keys=[blocked_vehicle_id], backref="incidents_suffered"
    )
    blocking_parking_record = db.relationship("ParkingRecord", backref="blocking_incidents")
    reported_by_user = db.relationship("User", backref="reported_incidents")

    def __repr__(self):
        return f"<BlockingIncident {self.blocking_vehicle_id} blocking {self.blocked_vehicle_id}>"



class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    blocking_incident_id = db.Column(db.Integer, db.ForeignKey("blocking_incidents.id"), nullable=False)
    recipient_resident_id = db.Column(db.Integer, db.ForeignKey("residents.id"), nullable=True)
    recipient_visitor_id = db.Column(db.Integer, db.ForeignKey("visitors.id"), nullable=True)
    channel = db.Column(db.String(10), nullable=False)  
    message = db.Column(db.String(500), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(15), default="sent")  

    blocking_incident = db.relationship("BlockingIncident", backref="notifications")
    recipient_resident = db.relationship("Resident", backref="notifications")
    recipient_visitor = db.relationship("Visitor", backref="notifications")

    def __repr__(self):
        return f"<Notification {self.id} ({self.status})>"



class MovementHistory(db.Model):
    __tablename__ = "movement_history"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey("checkpoints.id"), nullable=True)
    parking_record_id = db.Column(db.Integer, db.ForeignKey("parking_records.id"), nullable=True)
    action = db.Column(db.String(20), nullable=False)
    performed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    vehicle = db.relationship("Vehicle", backref="movement_history")
    checkpoint = db.relationship("Checkpoint", backref="movement_history")
    parking_record = db.relationship("ParkingRecord", backref="movement_history")
    performed_by_user = db.relationship("User", backref="actions_performed")

    def __repr__(self):
        return f"<MovementHistory {self.vehicle_id} {self.action}>"

