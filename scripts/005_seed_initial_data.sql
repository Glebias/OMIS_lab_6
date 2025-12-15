-- Seed initial data for testing

-- Insert standards
insert into public.standards (name, description) values
  ('ISO 9001', 'Quality management systems standard'),
  ('LEED', 'Leadership in Energy and Environmental Design'),
  ('BREEAM', 'Building Research Establishment Environmental Assessment Method');

-- Insert materials
insert into public.materials (name, type, texture) values
  ('Oak Wood', 'wood', 'natural grain'),
  ('Marble White', 'stone', 'polished smooth'),
  ('Concrete Gray', 'concrete', 'rough industrial'),
  ('Leather Brown', 'fabric', 'soft textured'),
  ('Glass Clear', 'glass', 'transparent smooth'),
  ('Steel Brushed', 'metal', 'brushed metallic'),
  ('Ceramic White', 'ceramic', 'glossy smooth'),
  ('Velvet Blue', 'fabric', 'soft plush');

-- Insert catalog
insert into public.catalog (name, description) values
  ('Modern Interior', 'Contemporary materials for modern spaces'),
  ('Classic Elegance', 'Traditional and timeless design materials'),
  ('Industrial Style', 'Raw and industrial aesthetic materials');

-- Link materials to catalogs
insert into public.catalog_materials (catalog_id, material_id)
select c.id, m.id from public.catalog c
cross join public.materials m
where c.name = 'Modern Interior' and m.name in ('Glass Clear', 'Steel Brushed', 'Concrete Gray');

insert into public.catalog_materials (catalog_id, material_id)
select c.id, m.id from public.catalog c
cross join public.materials m
where c.name = 'Classic Elegance' and m.name in ('Oak Wood', 'Marble White', 'Leather Brown');

-- Insert design norms
insert into public.design_norms (norm_id, name, status, normative_type, description) values
  ('NORM_001', 'Minimum Room Height', 'active', 'dimensional', 'Residential rooms must have minimum 2.4m ceiling height'),
  ('NORM_002', 'Fire Safety Exit', 'active', 'safety', 'Emergency exits must be clearly marked and accessible'),
  ('NORM_003', 'Natural Lighting', 'active', 'environmental', 'Living spaces require minimum natural light access'),
  ('NORM_004', 'Accessibility Standards', 'active', 'compliance', 'ADA compliance for wheelchair accessibility');
