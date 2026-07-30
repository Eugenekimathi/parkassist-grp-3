
from marshmallow import Schema, fields


class EstateSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    address = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    courts = fields.List(fields.Nested(lambda: CourtSchema(exclude=("estate",))), dump_only=True)
    checkpoints = fields.List(fields.Nested(lambda: CheckpointSchema(exclude=("estate",))), dump_only=True)


class CourtSchema(Schema):
    id = fields.Int(dump_only=True)
    estate_id = fields.Int(required=True)
    name = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    estate = fields.Nested(lambda: EstateSchema(only=("id", "name")), dump_only=True)
    residents = fields.List(fields.Nested(lambda: ResidentSchema(exclude=("court",))), dump_only=True)
    parking_slots = fields.List(fields.Nested(lambda: ParkingSlotSchema(exclude=("court",))), dump_only=True)
    parking_records = fields.List(fields.Nested(lambda: ParkingRecordSchema(exclude=("court",))), dump_only=True)


class CheckpointSchema(Schema):
    id = fields.Int(dump_only=True)
    estate_id = fields.Int(required=True)
    court_id = fields.Int(allow_none=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    estate = fields.Nested(lambda: EstateSchema(only=("id", "name")), dump_only=True)
    court = fields.Nested(lambda: CourtSchema(only=("id", "name")), dump_only=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str(required=True)
    phone = fields.Str(required=True)
    email = fields.Email(allow_none=True)
    role = fields.Str(required=True)
    checkpoint_id = fields.Int(allow_none=True)
    password_hash = fields.Str(required=True, load_only=True)
    created_at = fields.DateTime(dump_only=True)
    checkpoint = fields.Nested(lambda: CheckpointSchema(only=("id", "name")), dump_only=True)


class ResidentSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str(required=True)
    phone = fields.Str(required=True)
    email = fields.Email(allow_none=True)
    unit_number = fields.Str(required=True)
    court_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    court = fields.Nested(lambda: CourtSchema(only=("id", "name")), dump_only=True)
    visitors = fields.List(fields.Nested(lambda: VisitorSchema(exclude=("host_resident",))), dump_only=True)
    vehicles = fields.List(fields.Nested(lambda: VehicleSchema(exclude=("owner_resident", "owner_visitor",))), dump_only=True)


class VisitorSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str(required=True)
    phone = fields.Str(allow_none=True)
    id_number = fields.Str(allow_none=True)
    host_resident_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    host_resident = fields.Nested(lambda: ResidentSchema(only=("id", "full_name", "unit_number")), dump_only=True)
    vehicles = fields.List(fields.Nested(lambda: VehicleSchema(exclude=("owner_resident", "owner_visitor",))), dump_only=True)


class VehicleSchema(Schema):
    id = fields.Int(dump_only=True)
    plate_number = fields.Str(required=True)
    make = fields.Str(allow_none=True)
    model = fields.Str(allow_none=True)
    color = fields.Str(allow_none=True)
    vehicle_category = fields.Str(required=True)
    owner_resident_id = fields.Int(allow_none=True)
    owner_visitor_id = fields.Int(allow_none=True)
    registered_at_checkpoint_id = fields.Int(allow_none=True)
    registered_by_user_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    owner_resident = fields.Nested(lambda: ResidentSchema(only=("id", "full_name", "unit_number")), dump_only=True)
    owner_visitor = fields.Nested(lambda: VisitorSchema(only=("id", "full_name")), dump_only=True)
    registered_at_checkpoint = fields.Nested(lambda: CheckpointSchema(only=("id", "name")), dump_only=True)
    registered_by_user = fields.Nested(lambda: UserSchema(only=("id", "full_name")), dump_only=True)


class CheckpointLogSchema(Schema):
    id = fields.Int(dump_only=True)
    vehicle_id = fields.Int(required=True)
    checkpoint_id = fields.Int(required=True)
    verified_by_user_id = fields.Int(allow_none=True)
    action = fields.Str(required=True)
    timestamp = fields.DateTime(dump_only=True)
    notes = fields.Str(allow_none=True)
    vehicle = fields.Nested(lambda: VehicleSchema(only=("id", "plate_number")), dump_only=True)
    checkpoint = fields.Nested(lambda: CheckpointSchema(only=("id", "name")), dump_only=True)
    verified_by_user = fields.Nested(lambda: UserSchema(only=("id", "full_name")), dump_only=True)


class ParkingSlotSchema(Schema):
    id = fields.Int(dump_only=True)
    court_id = fields.Int(required=True)
    slot_number = fields.Str(required=True)
    is_occupied = fields.Bool()
    court = fields.Nested(lambda: CourtSchema(only=("id", "name")), dump_only=True)


class ParkingRecordSchema(Schema):
    id = fields.Int(dump_only=True)
    vehicle_id = fields.Int(required=True)
    court_id = fields.Int(required=True)
    parking_slot_id = fields.Int(allow_none=True)
    location_description = fields.Str(allow_none=True)
    parked_at = fields.DateTime(dump_only=True)
    left_at = fields.DateTime(allow_none=True)
    status = fields.Str()
    vehicle = fields.Nested(lambda: VehicleSchema(only=("id", "plate_number")), dump_only=True)
    court = fields.Nested(lambda: CourtSchema(only=("id", "name")), dump_only=True)
    parking_slot = fields.Nested(lambda: ParkingSlotSchema(only=("id", "slot_number")), dump_only=True)


class BlockingIncidentSchema(Schema):
    id = fields.Int(dump_only=True)
    blocking_vehicle_id = fields.Int(required=True)
    blocked_vehicle_id = fields.Int(required=True)
    blocking_parking_record_id = fields.Int(required=True)
    reported_by_user_id = fields.Int(allow_none=True)
    reported_at = fields.DateTime(dump_only=True)
    resolved_at = fields.DateTime(allow_none=True)
    status = fields.Str()
    blocking_vehicle = fields.Nested(lambda: VehicleSchema(only=("id", "plate_number")), dump_only=True)
    blocked_vehicle = fields.Nested(lambda: VehicleSchema(only=("id", "plate_number")), dump_only=True)
    blocking_parking_record = fields.Nested(lambda: ParkingRecordSchema(only=("id", "status")), dump_only=True)
    reported_by_user = fields.Nested(lambda: UserSchema(only=("id", "full_name")), dump_only=True)


class NotificationSchema(Schema):
    id = fields.Int(dump_only=True)
    blocking_incident_id = fields.Int(required=True)
    recipient_resident_id = fields.Int(allow_none=True)
    recipient_visitor_id = fields.Int(allow_none=True)
    channel = fields.Str(required=True)
    message = fields.Str(required=True)
    sent_at = fields.DateTime(dump_only=True)
    status = fields.Str()
    blocking_incident = fields.Nested(lambda: BlockingIncidentSchema(only=("id", "status")), dump_only=True)
    recipient_resident = fields.Nested(lambda: ResidentSchema(only=("id", "full_name")), dump_only=True)
    recipient_visitor = fields.Nested(lambda: VisitorSchema(only=("id", "full_name")), dump_only=True)


class MovementHistorySchema(Schema):
    id = fields.Int(dump_only=True)
    vehicle_id = fields.Int(required=True)
    checkpoint_id = fields.Int(allow_none=True)
    parking_record_id = fields.Int(allow_none=True)
    action = fields.Str(required=True)
    performed_by_user_id = fields.Int(allow_none=True)
    timestamp = fields.DateTime(dump_only=True)
    vehicle = fields.Nested(lambda: VehicleSchema(only=("id", "plate_number")), dump_only=True)
    checkpoint = fields.Nested(lambda: CheckpointSchema(only=("id", "name")), dump_only=True)
    parking_record = fields.Nested(lambda: ParkingRecordSchema(only=("id", "status")), dump_only=True)
    performed_by_user = fields.Nested(lambda: UserSchema(only=("id", "full_name")), dump_only=True)

