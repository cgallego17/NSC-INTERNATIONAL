-- Script SQL para crear las tablas de hoteles manualmente
-- Ejecutar solo si las migraciones no funcionan

-- Tabla locations_hotelroom
CREATE TABLE IF NOT EXISTS "locations_hotelroom" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "room_number" varchar(50) NOT NULL,
    "room_type" varchar(20) NOT NULL,
    "capacity" integer unsigned NOT NULL,
    "price_per_night" decimal NOT NULL,
    "description" text NOT NULL,
    "is_available" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "hotel_id" bigint NOT NULL REFERENCES "locations_hotel" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE UNIQUE INDEX IF NOT EXISTS "locations_hotelroom_hotel_id_room_number_uniq" ON "locations_hotelroom" ("hotel_id", "room_number");
CREATE INDEX IF NOT EXISTS "locations_hotelroom_hotel_id" ON "locations_hotelroom" ("hotel_id");

-- Tabla locations_hotelservice
CREATE TABLE IF NOT EXISTS "locations_hotelservice" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "service_name" varchar(200) NOT NULL,
    "service_type" varchar(30) NOT NULL,
    "description" text NOT NULL,
    "price" decimal NOT NULL,
    "is_per_person" bool NOT NULL,
    "is_per_night" bool NOT NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "hotel_id" bigint NOT NULL REFERENCES "locations_hotel" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "locations_hotelservice_hotel_id" ON "locations_hotelservice" ("hotel_id");

-- Tabla locations_hotelreservation
CREATE TABLE IF NOT EXISTS "locations_hotelreservation" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "guest_name" varchar(200) NOT NULL,
    "guest_email" varchar(254) NOT NULL,
    "guest_phone" varchar(20) NOT NULL,
    "number_of_guests" integer unsigned NOT NULL,
    "check_in" date NOT NULL,
    "check_out" date NOT NULL,
    "status" varchar(20) NOT NULL,
    "total_amount" decimal NOT NULL,
    "notes" text NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "hotel_id" bigint NOT NULL REFERENCES "locations_hotel" ("id") DEFERRABLE INITIALLY DEFERRED,
    "room_id" bigint NOT NULL REFERENCES "locations_hotelroom" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" bigint NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "locations_hotelreservation_hotel_id" ON "locations_hotelreservation" ("hotel_id");
CREATE INDEX IF NOT EXISTS "locations_hotelreservation_room_id" ON "locations_hotelreservation" ("room_id");
CREATE INDEX IF NOT EXISTS "locations_hotelreservation_user_id" ON "locations_hotelreservation" ("user_id");

-- Tabla locations_hotelreservationservice
CREATE TABLE IF NOT EXISTS "locations_hotelreservationservice" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "quantity" integer unsigned NOT NULL,
    "created_at" datetime NOT NULL,
    "reservation_id" bigint NOT NULL REFERENCES "locations_hotelreservation" ("id") DEFERRABLE INITIALLY DEFERRED,
    "service_id" bigint NOT NULL REFERENCES "locations_hotelservice" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE UNIQUE INDEX IF NOT EXISTS "locations_hotelreservationservice_reservation_id_service_id_uniq" ON "locations_hotelreservationservice" ("reservation_id", "service_id");
CREATE INDEX IF NOT EXISTS "locations_hotelreservationservice_reservation_id" ON "locations_hotelreservationservice" ("reservation_id");
CREATE INDEX IF NOT EXISTS "locations_hotelreservationservice_service_id" ON "locations_hotelreservationservice" ("service_id");

-- Registrar la migración como aplicada
INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES ('locations', '0010_create_hotel_room_service_reservation', datetime('now'));
