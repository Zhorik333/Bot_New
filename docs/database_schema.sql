-- Initial database design for Bot_New.
-- This file is a design artifact and can also be used as the first migration.

CREATE TABLE IF NOT EXISTS users (
    tg_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language TEXT NOT NULL DEFAULT 'ru' CHECK (language IN ('ru', 'en', 'sr')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS slots (
    id BIGSERIAL PRIMARY KEY,
    slot_date DATE NOT NULL,
    start_time TIME NOT NULL,
    starts_at TIMESTAMPTZ,
    duration_minutes INTEGER NOT NULL DEFAULT 10 CHECK (duration_minutes > 0),
    capacity INTEGER NOT NULL DEFAULT 1 CHECK (capacity > 0),
    is_blocked BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (slot_date, start_time)
);

CREATE TABLE IF NOT EXISTS bookings (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(tg_id) ON DELETE RESTRICT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    customer_name TEXT,
    phone TEXT,
    comment TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS booking_slots (
    booking_id BIGINT NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    slot_id BIGINT NOT NULL REFERENCES slots(id) ON DELETE RESTRICT,
    PRIMARY KEY (booking_id, slot_id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id BIGSERIAL PRIMARY KEY,
    booking_id BIGINT NOT NULL UNIQUE REFERENCES bookings(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(tg_id) ON DELETE RESTRICT,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'published', 'rejected')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    moderated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS i18n_texts (
    language TEXT NOT NULL CHECK (language IN ('ru', 'en', 'sr')),
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (language, key)
);

CREATE INDEX IF NOT EXISTS idx_slots_date_time ON slots(slot_date, start_time);
CREATE INDEX IF NOT EXISTS idx_slots_available ON slots(slot_date, start_time) WHERE is_blocked = false;
CREATE INDEX IF NOT EXISTS idx_bookings_user_status ON bookings(user_id, status);
CREATE INDEX IF NOT EXISTS idx_booking_slots_slot ON booking_slots(slot_id);
CREATE INDEX IF NOT EXISTS idx_reviews_status_created ON reviews(status, created_at DESC);

-- Availability should be calculated from booking_slots joined to bookings
-- where bookings.status IN ('active', 'completed').
-- Cancelled bookings keep history but free their slots.
