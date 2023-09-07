alter table user_profile add column is_qr_verified boolean default false;
alter table user_profile add column invalid_user_attempt INTEGER default 0;
alter table user_profile add column time_key_generator varchar(16) unique;
