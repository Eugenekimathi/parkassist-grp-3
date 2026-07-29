from marshmallow import fields, validate, validates, validates_schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app import db
from app.models import (
    Estate, Court, Checkpoint, User, Resident, Visitor,
    Vehicle, CheckpointLog, ParkingSlot, ParkingRecord,
    BlockingIncident, Notification, MovementHistory,
    ALLOWED_ROLES, ALLOWED_CHECKPOINT_TYPES, ALLOWED_VEHICLE_CATEGORIES,
    ALLOWED_LOG_ACTIONS, ALLOWED_PARKING_STATUSES, ALLOWED_INCIDENT_STATUSES,
    ALLOWED_NOTIFICATION_CHANNELS, ALLOWED_NOTIFICATION_STATUSES,
    ALLOWED_MOVEMENT_ACTIONS,
)


class EstateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Estate
        load_instance = True
        sqla_session = db.session

    name = fields.String(required=True, validate=validate.Length(min=2, max=255))


class CourtSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Court
        load_instance = True
        sqla_session = db.session
        include_fk = True

    name = fields.String(required=True, validate=validate.Length(min=1, max=100))


class CheckpointSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Checkpoint
        load_instance = True
        sqla_session = db.session
        include_fk = True

    type = fields.String(
        required=True,
        validate=validate.OneOf(ALLOWED_CHECKPOINT_TYPES),
    )


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_fk = True
        exclude = ("password_hash",)   # never serialize this out

    full_name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    phone = fields.String(required=True, validate=validate.Length(min=9, max=20))
    email = fields.Email(allow_none=True)
    role = fields.String(required=True, validate=validate.OneOf(ALLOWED_ROLES))


class ResidentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Resident
        load_instance = True
        sqla_session = db.session
        include_fk = True

    full_name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    phone = fields.String(required=True, validate=validate.Length(min=9, max=20))
    email = fields.Email(allow_none=True)
    unit_number = fields.String(required=True, validate=validate.Length(min=1, max=50))

    # Embed this resident's vehicles, but cut the cycle: the nested Vehicle
    # must not re-embed its owner_resident, which would point right back here.
    vehicles = fields.Nested(
        "VehicleSchema",
        many=True,
        dump_only=True,
        exclude=("owner_resident", "owner_visitor"),
    )


class VisitorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Visitor
        load_instance = True
        sqla_session = db.session
        include_fk = True

    full_name = fields.String(required=True, validate=validate.Length(min=1, max=255))

    # Show which resident hosts this visitor, without that resident
    # re-embedding its full visitor list — only summary fields needed.
    host_resident = fields.Nested(
        "ResidentSchema",
        dump_only=True,
        only=("id", "full_name", "unit_number"),
    )

    vehicles = fields.Nested(
        "VehicleSchema",
        many=True,
        dump_only=True,
        exclude=("owner_resident", "owner_visitor"),
    )


class VehicleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        load_instance = True
        sqla_session = db.session
        include_fk = True

    plate_number = fields.String(required=True, validate=validate.Length(min=4, max=20))
    vehicle_category = fields.String(
        required=True, validate=validate.OneOf(ALLOWED_VEHICLE_CATEGORIES)
    )

    # Embed the owner directly instead of forcing a second lookup by
    # owner_resident_id/owner_visitor_id — each side excludes "vehicles"
    # so a Resident's own vehicle list doesn't try to re-nest itself.
    owner_resident = fields.Nested(
        "ResidentSchema", dump_only=True, exclude=("vehicles",), allow_none=True
    )
    owner_visitor = fields.Nested(
        "VisitorSchema", dump_only=True, exclude=("vehicles",), allow_none=True
    )

    @validates_schema
    def validate_single_owner(self, data, **kwargs):
        # Mirrors the CheckConstraint in models.py, but gives a clean
        # error message before the row ever reaches the database.
        resident_id = data.get("owner_resident_id")
        visitor_id = data.get("owner_visitor_id")
        if bool(resident_id) == bool(visitor_id):
            raise ValidationError(
                "Exactly one of owner_resident_id or owner_visitor_id must be set."
            )


class CheckpointLogSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CheckpointLog
        load_instance = True
        sqla_session = db.session
        include_fk = True

    action = fields.String(required=True, validate=validate.OneOf(ALLOWED_LOG_ACTIONS))

    vehicle = fields.Nested("VehicleSchema", dump_only=True, exclude=("checkpoint_logs",))
    checkpoint = fields.Nested("CheckpointSchema", dump_only=True, exclude=("logs",))


class ParkingSlotSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ParkingSlot
        load_instance = True
        sqla_session = db.session
        include_fk = True

    slot_number = fields.String(required=True, validate=validate.Length(min=1, max=20))


class ParkingRecordSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ParkingRecord
        load_instance = True
        sqla_session = db.session
        include_fk = True

    status = fields.String(validate=validate.OneOf(ALLOWED_PARKING_STATUSES))

    vehicle = fields.Nested("VehicleSchema", dump_only=True, exclude=("parking_records",))
    parking_slot = fields.Nested(
        "ParkingSlotSchema", dump_only=True, exclude=("parking_records",), allow_none=True
    )

    @validates_schema
    def validate_left_after_parked(self, data, **kwargs):
        # Mirrors the CheckConstraint check_left_after_parked
        parked_at = data.get("parked_at")
        left_at = data.get("left_at")
        if left_at and parked_at and left_at <= parked_at:
            raise ValidationError("left_at must be after parked_at.")


class BlockingIncidentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BlockingIncident
        load_instance = True
        sqla_session = db.session
        include_fk = True

    status = fields.String(validate=validate.OneOf(ALLOWED_INCIDENT_STATUSES))

    # Same Vehicle model nested twice under different field names — each
    # excludes the specific backref pointing back to *this* relationship,
    # not "vehicles" in general.
    blocking_vehicle = fields.Nested(
        "VehicleSchema", dump_only=True, exclude=("incidents_caused",)
    )
    blocked_vehicle = fields.Nested(
        "VehicleSchema", dump_only=True, exclude=("incidents_suffered",)
    )

    @validates_schema
    def validate_distinct_vehicles(self, data, **kwargs):
        # Mirrors check_incident_distinct_vehicles
        blocking_id = data.get("blocking_vehicle_id")
        blocked_id = data.get("blocked_vehicle_id")
        if blocking_id and blocked_id and blocking_id == blocked_id:
            raise ValidationError("blocking_vehicle_id and blocked_vehicle_id must differ.")


class NotificationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        load_instance = True
        sqla_session = db.session
        include_fk = True

    channel = fields.String(
        required=True, validate=validate.OneOf(ALLOWED_NOTIFICATION_CHANNELS)
    )
    status = fields.String(validate=validate.OneOf(ALLOWED_NOTIFICATION_STATUSES))
    message = fields.String(required=True, validate=validate.Length(min=1, max=500))

    blocking_incident = fields.Nested(
        "BlockingIncidentSchema", dump_only=True, exclude=("notifications",)
    )

    @validates_schema
    def validate_single_recipient(self, data, **kwargs):
        # Mirrors check_notification_single_recipient
        resident_id = data.get("recipient_resident_id")
        visitor_id = data.get("recipient_visitor_id")
        if bool(resident_id) == bool(visitor_id):
            raise ValidationError(
                "Exactly one of recipient_resident_id or recipient_visitor_id must be set."
            )


class MovementHistorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MovementHistory
        load_instance = True
        sqla_session = db.session
        include_fk = True

    action = fields.String(required=True, validate=validate.OneOf(ALLOWED_MOVEMENT_ACTIONS))


# Single / many instances for each schema
estate_schema, estates_schema = EstateSchema(), EstateSchema(many=True)
court_schema, courts_schema = CourtSchema(), CourtSchema(many=True)
checkpoint_schema, checkpoints_schema = CheckpointSchema(), CheckpointSchema(many=True)
user_schema, users_schema = UserSchema(), UserSchema(many=True)
resident_schema, residents_schema = ResidentSchema(), ResidentSchema(many=True)
visitor_schema, visitors_schema = VisitorSchema(), VisitorSchema(many=True)
vehicle_schema, vehicles_schema = VehicleSchema(), VehicleSchema(many=True)
checkpoint_log_schema, checkpoint_logs_schema = CheckpointLogSchema(), CheckpointLogSchema(many=True)
parking_slot_schema, parking_slots_schema = ParkingSlotSchema(), ParkingSlotSchema(many=True)
parking_record_schema, parking_records_schema = ParkingRecordSchema(), ParkingRecordSchema(many=True)
blocking_incident_schema, blocking_incidents_schema = BlockingIncidentSchema(), BlockingIncidentSchema(many=True)
notification_schema, notifications_schema = NotificationSchema(), NotificationSchema(many=True)
movement_history_schema, movement_histories_schema = MovementHistorySchema(), MovementHistorySchema(many=True)