CREATE TABLE users(
    id integer primary key autoincrement,
    username text not null unique,
    hash text not null,
    created_at datetime default current_timestamp
);

CREATE TABLE words(
    id integer primary key autoincrement,
    word text not null unique
);

CREATE TABLE races(
    id integer primary key autoincrement,
    user_id integer not null,
    duration_mode integer not null,
    wpm real not null,
    accuracy real not null, 
    correct_chars integer not null,
    completed_at TIMESTAMP default current_timestamp,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE INDEX idx_races_leaderboard ON races(duration_mode, wpm DESC);