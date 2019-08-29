
CREATE TABLE participants (
    id integer primary key autoincrement not null,
    userhash text not null,
    gender text not null,
    age integer not null, 
    handedness text not null,
    created text not null
);

CREATE TABLE trials (
    id integer primary key autoincrement not null,
    participant_id integer not null references participants(id),
    block_num integer not null,
    trial_num integer not null,
    practicing boolean not null,
    tone_trial boolean not null,
    tone_onset integer not null,
    cue_type text not null,
    congruent boolean not null,
    target_location text not null,
    target_direction text not null,
    accuracy integer not null,
    response text not null,
    rt integer not null
);
