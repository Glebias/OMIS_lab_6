-- This script should be run in Supabase SQL Editor to disable email confirmation
-- Go to: Authentication > Settings in Supabase Dashboard
-- Or run this if you have access to update auth config

-- Note: These settings need to be changed in Supabase Dashboard:
-- 1. Go to Authentication > Settings
-- 2. Set "Enable email confirmations" to OFF
-- 3. Set "Enable email signup" to ON

-- For development, you can also use this query to confirm all existing users:
-- WARNING: Only use in development!

-- Update all unconfirmed users to confirmed (DEVELOPMENT ONLY)
update auth.users
set email_confirmed_at = now(),
    confirmed_at = now()
where email_confirmed_at is null;

-- Optional: Create a function to auto-confirm new users
create or replace function public.auto_confirm_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  -- Auto-confirm the user
  update auth.users
  set email_confirmed_at = now(),
      confirmed_at = now()
  where id = new.id and email_confirmed_at is null;
  
  return new;
end;
$$;

-- Create trigger to auto-confirm users on creation
drop trigger if exists on_auth_user_auto_confirm on auth.users;

create trigger on_auth_user_auto_confirm
  after insert on auth.users
  for each row
  execute function public.auto_confirm_user();
