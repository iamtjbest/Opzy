-- Opzy database schema (v1)
-- Run this in the Supabase SQL editor. Matches DATABASE_SCHEMA.md exactly.

create extension if not exists "uuid-ossp";

-- USERS
create table users (
  id uuid primary key default uuid_generate_v4(),
  email text unique not null,
  password_hash text not null,
  notification_cadence text not null default 'daily'
    check (notification_cadence in ('instant', 'daily', 'weekly')),
  notification_channel text not null default 'email'
    check (notification_channel in ('email', 'whatsapp')),
  created_at timestamptz not null default now()
);

-- PROFILES
create table profiles (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references users(id) on delete cascade,
  education_level text,
  field_of_study text,
  location text,
  updated_at timestamptz not null default now()
);
create unique index profiles_user_id_idx on profiles(user_id);

-- PROFILE SKILLS (many-to-many via tags)
create table profile_skills (
  id uuid primary key default uuid_generate_v4(),
  profile_id uuid not null references profiles(id) on delete cascade,
  skill text not null
);
create index profile_skills_profile_id_idx on profile_skills(profile_id);

-- PROFILE INTERESTS (opportunity types selected at onboarding)
create table profile_interests (
  id uuid primary key default uuid_generate_v4(),
  profile_id uuid not null references profiles(id) on delete cascade,
  opportunity_type text not null
    check (opportunity_type in ('job', 'internship', 'scholarship', 'fellowship', 'grant', 'hackathon', 'competition'))
);
create index profile_interests_profile_id_idx on profile_interests(profile_id);

-- OPPORTUNITIES (maps directly to OPZY_SOURCE_TRACKING.xlsx columns)
create table opportunities (
  id uuid primary key default uuid_generate_v4(),
  title text not null,
  organization text,
  category text not null
    check (category in ('job', 'internship', 'scholarship', 'fellowship', 'grant', 'hackathon', 'competition')),
  geography text,
  description text,
  deadline date,
  eligibility_notes text,
  application_url text,
  source_url text,
  quality_rating integer check (quality_rating between 1 and 5),
  verified boolean not null default false,
  status text not null default 'active'
    check (status in ('active', 'expired', 'removed')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index opportunities_status_idx on opportunities(status);
create index opportunities_category_idx on opportunities(category);
create index opportunities_deadline_idx on opportunities(deadline);

-- OPPORTUNITY MATCHES (output of the matching logic)
create table opportunity_matches (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references users(id) on delete cascade,
  opportunity_id uuid not null references opportunities(id) on delete cascade,
  match_score integer not null check (match_score between 0 and 100),
  match_reasons text[] not null default '{}',
  created_at timestamptz not null default now()
);
create index opportunity_matches_user_id_idx on opportunity_matches(user_id);
create unique index opportunity_matches_user_opp_idx on opportunity_matches(user_id, opportunity_id);

-- USER OPPORTUNITY ACTIONS (save / dismiss / applied, one row per action)
create table user_opportunity_actions (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references users(id) on delete cascade,
  opportunity_id uuid not null references opportunities(id) on delete cascade,
  action text not null check (action in ('saved', 'dismissed', 'applied')),
  dismiss_reason text,
  created_at timestamptz not null default now()
);
create index user_opportunity_actions_user_id_idx on user_opportunity_actions(user_id);
create index user_opportunity_actions_opportunity_id_idx on user_opportunity_actions(opportunity_id);

-- Row Level Security: on by default in Supabase once enabled.
-- Enable + add policies once auth is wired up, so this doesn't silently expose data.
-- Left off here on purpose rather than guessing policies before real auth exists.
