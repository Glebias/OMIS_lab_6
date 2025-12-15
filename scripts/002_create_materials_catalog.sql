-- Materials and Catalog system based on ER diagrams

-- Standards table
create table if not exists public.standards (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.standards enable row level security;

create policy "anyone_can_view_standards"
  on public.standards for select
  using (true);

-- Materials table
create table if not exists public.materials (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  type text not null,
  texture text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.materials enable row level security;

create policy "anyone_can_view_materials"
  on public.materials for select
  using (true);

-- Catalog table
create table if not exists public.catalog (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.catalog enable row level security;

create policy "anyone_can_view_catalog"
  on public.catalog for select
  using (true);

-- Catalog materials relationship
create table if not exists public.catalog_materials (
  catalog_id uuid not null references public.catalog(id) on delete cascade,
  material_id uuid not null references public.materials(id) on delete cascade,
  primary key (catalog_id, material_id)
);

alter table public.catalog_materials enable row level security;

create policy "anyone_can_view_catalog_materials"
  on public.catalog_materials for select
  using (true);

-- Catalog standards relationship
create table if not exists public.catalog_standards (
  catalog_id uuid not null references public.catalog(id) on delete cascade,
  standard_id uuid not null references public.standards(id) on delete cascade,
  primary key (catalog_id, standard_id)
);

alter table public.catalog_standards enable row level security;

create policy "anyone_can_view_catalog_standards"
  on public.catalog_standards for select
  using (true);
