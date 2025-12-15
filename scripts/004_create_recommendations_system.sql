-- Recommendations system based on class diagrams

create table if not exists public.recommendations (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  type text not null,
  title text not null,
  description text not null,
  data jsonb, -- Additional recommendation data
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.recommendations enable row level security;

create policy "users_can_view_project_recommendations"
  on public.recommendations for select
  using (
    exists (
      select 1 from public.projects
      where projects.id = recommendations.project_id
      and projects.user_id = auth.uid()
    )
  );

create policy "users_can_create_project_recommendations"
  on public.recommendations for insert
  with check (
    exists (
      select 1 from public.projects
      where projects.id = project_id
      and projects.user_id = auth.uid()
    )
  );

-- Planning analysis subsystem
create table if not exists public.layout_analysis (
  id uuid primary key default gen_random_uuid(),
  room_id uuid not null references public.rooms(id) on delete cascade,
  analysis_type text not null,
  result jsonb not null,
  compliance_factors jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.layout_analysis enable row level security;

create policy "users_can_view_room_analysis"
  on public.layout_analysis for select
  using (
    exists (
      select 1 from public.rooms
      join public.projects on projects.id = rooms.project_id
      where rooms.id = layout_analysis.room_id
      and projects.user_id = auth.uid()
    )
  );

-- Design norms
create table if not exists public.design_norms (
  id uuid primary key default gen_random_uuid(),
  norm_id text not null unique,
  name text not null,
  status text not null,
  normative_type text not null,
  description text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.design_norms enable row level security;

create policy "anyone_can_view_design_norms"
  on public.design_norms for select
  using (true);
