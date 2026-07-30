from datetime import datetime
from sqlalchemy.orm import validates
from app import db 

ALLOWED_ROLES = ["security", "admin", "supervisor"]
ALLOWED_CHECKPOINT_TYPES = ["main_gate", "court_gate"]
ALLOWED_VEHICLE_CATEGORIES = ["resident", "visitor"]
ALLOWED_LOG_ACTIONS = ["entry", "exit"]
ALLOWED_PARKING_STATUSES = ["parked", "moved", "left"]
ALLOWED_INCIDENT_STATUSES = ["pending","notified" ,"resolved"]
ALLOWED_NOTIFICATION_CHANNELS = ["sms", "call", "in-app"]
ALLOWED_NOTIFICATION_STATUSES = ["sent", "delivered", "failed","acknowledged"]
ALLOWED_MOVEMENT_ACTIONS = [ 'registered', 'entry', 'exit', 'parked', 'moved', 'blocking_reported', 'resolved']

def _non_empty(value, field_name):
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")
    return value.strip()

def _valid_phone(value):
    digits = value.replace("+", "").replace(" ", "").replace("-", "")
    if not digits.isdigit() or len(digits) < 9:
        raise ValueError("phone must be a valid number (at least 9 digits).")
    return value

class Estate(db.Model):
    __tablename__ = "estates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    courts = db.relationship("Court", backref="estate")
    checkpoints = db.relationship("Checkpoint", backref="estate")

    __table_args__ = (
        db.UniqueConstraint("name", name="uq_estate_name"),
    )

    @validates("name")
    def validate_name(self, key, value):
        return _non_empty(value, "name")

    def __repr__(self):
        return f"<Estate {self.name}>"


class Court(db.Model):
    __tablename__ = "courts"

    id = db.Column(db.Integer, primary_key=True)
    estate_id = db.Column(db.Integer, db.ForeignKey("estates.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("estate_id", "name", name="uq_court_name_per_estate"),
    )

    @validates("name")
    def validate_name(self, key, value):
        return _non_empty(value, "name")

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

    __table_args__ = (
        db.CheckConstraint(
            "type IN ('main_gate','court_gate')", name="check_checkpoint_type_valid"
        ),
    )

    court = db.relationship("Court", backref="checkpoints")

    @validates("name")
    def validate_name(self, key, value):
        return _non_empty(value, "name")

    @validates("type")
    def validate_type(self, key, value):
        if value not in ALLOWED_CHECKPOINT_TYPES:
            raise ValueError(f"type must be one of {ALLOWED_CHECKPOINT_TYPES}")
        return value

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

    @validates("full_name")
    def validate_full_name(self, key, value):
        return _non_empty(value, "full_name")

    @validates("phone")
    def validate_phone(self, key, value):
        return _valid_phone(value)

    @validates("role")
    def validate_role(self, key, value):
        if value not in ALLOWED_ROLES:
            raise ValueError(f"role must be one of {ALLOWED_ROLES}")
        return value

    def __repr__(self):
        return f"<User {self.full_name}>"


class Resident(db.Model):
    __tablename__ = "residents"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255))
    unit_number = db.Column(db.String(50), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey("courts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    court = db.relationship("Court", backref="residents")

    @validates("full_name")
    def validate_full_name(self, key, value):
        return _non_empty(value, "full_name")

    @validates("phone")
    def validate_phone(self, key, value):
        return _valid_phone(value)

    @validates("unit_number")
    def validate_unit_number(self, key, value):
        return _non_empty(value, "unit_number")

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

    @validates("full_name")
    def validate_full_name(self, key, value):
        return _non_empty(value, "full_name")

    @validates("phone")
    def validate_phone(self, key, value):
        if value:
            return _valid_phone(value)
        return value

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
    __table_args__ = (
        db.CheckConstraint(
            "(owner_resident_id IS NOT NULL AND owner_visitor_id IS NULL) OR "
            "(owner_resident_id IS NULL AND owner_visitor_id IS NOT NULL)",
            name="check_vehicle_single_owner_type",
        ),
    )
    owner_resident = db.relationship("Resident", backref="vehicles")
    owner_visitor = db.relationship("Visitor", backref="vehicles")
    registered_at_checkpoint = db.relationship("Checkpoint", backref="vehicles_registered")
    registered_by_user = db.relationship("User", backref="vehicles_registered")

    @validates("plate_number")
    def validate_plate_number(self, key, value):
        cleaned = _non_empty(value, "plate_number").upper()
        if len(cleaned) < 4:
            raise ValueError("plate_number looks too short to be valid.")
        return cleaned

    @validates("vehicle_category")
    def validate_category(self, key, value):
        if value not in ALLOWED_VEHICLE_CATEGORIES:
            raise ValueError(f"vehicle_category must be one of {ALLOWED_VEHICLE_CATEGORIES}")
        return value

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

    __table_args__ = (
        db.CheckConstraint("action IN ('entry','exit')", name="check_log_action_valid"),
    )

    vehicle = db.relationship("Vehicle", backref="checkpoint_logs")
    checkpoint = db.relationship("Checkpoint", backref="logs")
    verified_by_user = db.relationship("User", backref="verified_logs")

    @validates("action")
    def validate_action(self, key, value):
        if value not in ALLOWED_LOG_ACTIONS:
            raise ValueError(f"action must be one of {ALLOWED_LOG_ACTIONS}")
        return value

    def __repr__(self):
        return f"<CheckpointLog {self.vehicle_id} {self.action}>"


class ParkingSlot(db.Model):
    __tablename__ = "parking_slots"

    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey("courts.id"), nullable=False)
    slot_number = db.Column(db.String(20), nullable=False)
    is_occupied = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("court_id", "slot_number", name="uq_slot_number_per_court"),
    )

    court = db.relationship("Court", backref="parking_slots")

    @validates("slot_number")
    def validate_slot_number(self, key, value):
        return _non_empty(value, "slot_number")

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
    status = db.Column(db.String(10), default="parked", nullable=False)

    __table_args__ = (
        db.CheckConstraint(
            "left_at IS NULL OR left_at > parked_at", name="check_left_after_parked"
        ),
        db.CheckConstraint(
            "status IN ('parked','moved','left')", name="check_parking_status_valid"
        ),
    )

    vehicle = db.relationship("Vehicle", backref="parking_records")
    court = db.relationship("Court", backref="parking_records")
    parking_slot = db.relationship("ParkingSlot", backref="parking_records")

    @validates("status")
    def validate_status(self, key, value):
        if value not in ALLOWED_PARKING_STATUSES:
            raise ValueError(f"status must be one of {ALLOWED_PARKING_STATUSES}")
        return value

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
    status = db.Column(db.String(10), default="pending", nullable=False)

    __table_args__ = (
        db.CheckConstraint(
            "blocking_vehicle_id != blocked_vehicle_id",
            name="check_incident_distinct_vehicles",
        ),
        db.CheckConstraint(
            "resolved_at IS NULL OR resolved_at >= reported_at",
            name="check_resolved_after_reported",
        ),
    )

    blocking_vehicle = db.relationship(
        "Vehicle", foreign_keys=[blocking_vehicle_id], backref="incidents_caused"
    )
    blocked_vehicle = db.relationship(
        "Vehicle", foreign_keys=[blocked_vehicle_id], backref="incidents_suffered"
    )
    blocking_parking_record = db.relationship("ParkingRecord", backref="blocking_incidents")
    reported_by_user = db.relationship("User", backref="reported_incidents")

    @validates("status")
    def validate_status(self, key, value):
        if value not in ALLOWED_INCIDENT_STATUSES:
            raise ValueError(f"status must be one of {ALLOWED_INCIDENT_STATUSES}")
        return value

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
    status = db.Column(db.String(15), default="sent", nullable=False)

    __table_args__ = (
        db.CheckConstraint(
            "(recipient_resident_id IS NOT NULL AND recipient_visitor_id IS NULL) OR "
            "(recipient_resident_id IS NULL AND recipient_visitor_id IS NOT NULL)",
            name="check_notification_single_recipient",
        ),
    )

    blocking_incident = db.relationship("BlockingIncident", backref="notifications")
    recipient_resident = db.relationship("Resident", backref="notifications")
    recipient_visitor = db.relationship("Visitor", backref="notifications")

    @validates("channel")
    def validate_channel(self, key, value):
        if value not in ALLOWED_NOTIFICATION_CHANNELS:
            raise ValueError(f"channel must be one of {ALLOWED_NOTIFICATION_CHANNELS}")
        return value

    @validates("status")
    def validate_status(self, key, value):
        if value not in ALLOWED_NOTIFICATION_STATUSES:
            raise ValueError(f"status must be one of {ALLOWED_NOTIFICATION_STATUSES}")
        return value

    @validates("message")
    def validate_message(self, key, value):
        return _non_empty(value, "message")

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

    @validates("action")
    def validate_action(self, key, value):
        if value not in ALLOWED_MOVEMENT_ACTIONS:
            raise ValueError(f"action must be one of {ALLOWED_MOVEMENT_ACTIONS}")
        return value

    def __repr__(self):
        return f"<MovementHistory {self.vehicle_id} {self.action}>"
