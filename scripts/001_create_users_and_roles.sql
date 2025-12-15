-- Users and roles system based on ER diagram
-- Create profiles table with role-based access

create type user_role as enum ('client', 'designer', 'manager', 'consultant');

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null,
  email text not null,
  role user_role not null default 'client',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS
alter table public.profiles enable row level security;

-- Policies for profiles
create policy "users_can_view_own_profile"
  on public.profiles for select
  using (auth.uid() = id);

create policy "users_can_update_own_profile"
  on public.profiles for update
  using (auth.uid() = id);

create policy "users_can_insert_own_profile"
  on public.profiles for insert
  with check (auth.uid() = id);

-- Create trigger to auto-create profile on signup
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, full_name, email, role)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'full_name', 'User'),
    new.email,
    coalesce((new.raw_user_meta_data ->> 'role')::user_role, 'client')
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;

create trigger on_auth_user_created
  after insert on auth.users
  for each row
  execute function public.handle_new_user();

-- Comments table
create table if not exists public.comments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  text text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.comments enable row level security;

create policy "users_can_view_all_comments"
  on public.comments for select
  using (true);

create policy "users_can_create_comments"
  on public.comments for insert
  with check (auth.uid() = user_id);
