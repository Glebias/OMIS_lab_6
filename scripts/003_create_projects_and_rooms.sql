-- Projects, Rooms and Models based on ER diagrams

-- Projects table
create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  name text not null,
  description text,
  status text not null default 'active',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.projects enable row level security;

create policy "users_can_view_own_projects"
  on public.projects for select
  using (auth.uid() = user_id);

create policy "users_can_create_projects"
  on public.projects for insert
  with check (auth.uid() = user_id);

create policy "users_can_update_own_projects"
  on public.projects for update
  using (auth.uid() = user_id);

create policy "users_can_delete_own_projects"
  on public.projects for delete
  using (auth.uid() = user_id);

-- Rooms table
create table if not exists public.rooms (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  name text not null,
  dimensions jsonb not null, -- {width, height, length}
  location text,
  lighting text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.rooms enable row level security;

create policy "users_can_view_project_rooms"
  on public.rooms for select
  using (
    exists (
      select 1 from public.projects
      where projects.id = rooms.project_id
      and projects.user_id = auth.uid()
    )
  );

create policy "users_can_create_project_rooms"
  on public.rooms for insert
  with check (
    exists (
      select 1 from public.projects
      where projects.id = project_id
      and projects.user_id = auth.uid()
    )
  );

-- 3D Models table
create table if not exists public.models (
  id uuid primary key default gen_random_uuid(),
  room_id uuid references public.rooms(id) on delete cascade,
  model_id text not null,
  name text not null,
  dimensions jsonb not null,
  format text not null,
  file_url text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.models enable row level security;

create policy "users_can_view_room_models"
  on public.models for select
  using (
    exists (
      select 1 from public.rooms
      join public.projects on projects.id = rooms.project_id
      where rooms.id = models.room_id
      and projects.user_id = auth.uid()
    )
  );

-- Model materials relationship
create table if not exists public.model_materials (
  model_id uuid not null references public.models(id) on delete cascade,
  material_id uuid not null references public.materials(id) on delete cascade,
  primary key (model_id, material_id)
);

alter table public.model_materials enable row level security;

create policy "users_can_view_model_materials"
  on public.model_materials for select
  using (
    exists (
      select 1 from public.models
      join public.rooms on rooms.id = models.room_id
      join public.projects on projects.id = rooms.project_id
      where models.id = model_materials.model_id
      and projects.user_id = auth.uid()
    )
  );
