-- Seed data for redparts_shop

-- Countries (safe upsert)
INSERT INTO countries (code, name, phone_code, currency_code) VALUES
('US','United States','+1','USD'),
('RU','Russia','+7','RUB'),
('DE','Germany','+49','EUR'),
('JP','Japan','+81','JPY'),
('KR','South Korea','+82','KRW'),
('FR','France','+33','EUR')
ON CONFLICT (code) DO NOTHING;

-- Brands
INSERT INTO brands (slug, name, country_code, website, is_active) VALUES
('toyota','Toyota','JP','https://www.toyota-global.com',true),
('ford','Ford','US','https://www.ford.com',true),
('bosch','Bosch','DE','https://www.bosch.com',true),
('ngk','NGK','JP','https://www.ngkntk.com',true),
('continental','Continental','DE','https://www.continental.com',true),
('denso','Denso','JP','https://www.denso.com',true),
('kyb','KYB','JP','https://www.kyb.com',true),
('mahle','MAHLE','DE','https://www.mahle.com',true),
('gates','Gates','US','https://www.gates.com',true),
('valeo','Valeo','FR','https://www.valeo.com',true)
ON CONFLICT (slug) DO NOTHING;

-- Categories (match frontend demo slugs)
INSERT INTO categories (parent_id, name, slug, description, image, layout, sort_order, is_active) VALUES
(NULL,'Tires & Wheels','tires-wheels',NULL,NULL,'products',1,true),
(NULL,'Interior Parts','interior-parts',NULL,NULL,'products',2,true),
(NULL,'Engine & Drivetrain','engine-drivetrain',NULL,NULL,'products',3,true),
(NULL,'Hand Tools','hand-tools',NULL,NULL,'products',4,true),
(NULL,'Power Tools','power-tools',NULL,NULL,'products',5,true)
ON CONFLICT (slug) DO NOTHING;

-- Subcategories flat insert (names in RU can be applied later via update if needed)
INSERT INTO categories (parent_id, name, slug, layout, sort_order, is_active) VALUES
(NULL,'Headlights','headlights','products',10,true),
(NULL,'Tail Lights','tail-lights','products',11,true),
(NULL,'Fog Lights','fog-lights','products',12,true),
(NULL,'Turn Signals','turn-signals','products',13,true),
(NULL,'Switches & Relays','switches-relays','products',14,true),
(NULL,'Corner Lights','corner-lights','products',15,true),
(NULL,'Body Parts','body-parts','products',16,true),
(NULL,'Suspension','suspension','products',17,true),
(NULL,'Steering','steering','products',18,true),
(NULL,'Fuel Systems','fuel-systems','products',19,true),
(NULL,'Transmission','transmission','products',20,true),
(NULL,'Air Filters','air-filters','products',21,true),
(NULL,'Floor Mats','floor-mats','products',22,true),
(NULL,'Gauges','gauges','products',23,true),
(NULL,'Consoles & Organizers','consoles-organizers','products',24,true),
(NULL,'Mobile Electronics','mobile-electronics','products',25,true),
(NULL,'Steering Wheels','steering-wheels','products',26,true),
(NULL,'Cargo Accessories','cargo-accessories','products',27,true),
(NULL,'Repair Manuals','repair-manuals','products',28,true),
(NULL,'Car Care','car-care','products',29,true),
(NULL,'Code Readers','code-readers','products',30,true),
(NULL,'Tool Boxes','tool-boxes','products',31,true),
(NULL,'Brake Discs','brake-discs','products',32,true),
(NULL,'Wheel Hubs','wheel-hubs','products',33,true),
(NULL,'Air Suspension','air-suspension','products',34,true),
(NULL,'Ball Joints','ball-joints','products',35,true),
(NULL,'Brake Pad Sets','brake-pad-sets','products',36,true),
(NULL,'Bumpers','bumpers','products',37,true),
(NULL,'Hoods','hoods','products',38,true),
(NULL,'Grilles','grilles','products',39,true),
(NULL,'Door Handles','door-handles','products',40,true),
(NULL,'Car Covers','car-covers','products',41,true),
(NULL,'Tailgates','tailgates','products',42,true),
(NULL,'Oxygen Sensors','oxygen-sensors','products',43,true),
(NULL,'Heating','heating','products',44,true),
(NULL,'Exhaust','exhaust','products',45,true),
(NULL,'Cranks & Pistons','cranks-pistons','products',46,true)
ON CONFLICT (slug) DO NOTHING;

-- Build hierarchy via parent slugs
-- Lighting children under headlights-lighting
UPDATE categories c
SET parent_id = p.id
FROM categories p
WHERE p.slug = 'headlights-lighting'
  AND c.slug IN ('headlights','tail-lights','fog-lights','turn-signals','switches-relays','corner-lights');

-- Interior children under interior-parts
UPDATE categories c
SET parent_id = p.id
FROM categories p
WHERE p.slug = 'interior-parts'
  AND c.slug IN ('floor-mats','gauges','consoles-organizers','mobile-electronics','steering-wheels','cargo-accessories');

-- Engine & Drivetrain children
UPDATE categories c
SET parent_id = p.id
FROM categories p
WHERE p.slug = 'engine-drivetrain'
  AND c.slug IN ('air-filters','oxygen-sensors','heating','exhaust','cranks-pistons','fuel-systems','transmission');

-- Tools & Garage children
UPDATE categories c
SET parent_id = p.id
FROM categories p
WHERE p.slug = 'tools-garage'
  AND c.slug IN ('repair-manuals','car-care','code-readers','tool-boxes','body-parts','suspension','steering','brake-discs','wheel-hubs','air-suspension','ball-joints','brake-pad-sets');

-- Vehicle makes
INSERT INTO vehicle_makes (name, slug, country_code, is_active) VALUES
('Toyota','toyota','JP',true),
('Ford','ford','US',true),
('Volkswagen','volkswagen','DE',true),
('BMW','bmw','DE',true)
ON CONFLICT (slug) DO NOTHING;

-- Vehicle models (basic)
INSERT INTO vehicle_models (make_id, name, slug, year_from, year_to, is_active)
VALUES
((SELECT id FROM vehicle_makes WHERE slug='toyota'),'Camry','camry',2007,2024,true),
((SELECT id FROM vehicle_makes WHERE slug='toyota'),'Corolla','corolla',2006,2024,true),
((SELECT id FROM vehicle_makes WHERE slug='ford'),'Focus','focus',2005,2018,true),
((SELECT id FROM vehicle_makes WHERE slug='bmw'),'3 Series','3-series',2006,2024,true)
ON CONFLICT DO NOTHING;

-- Product examples
-- Use brand_id via subselect; prices in USD
INSERT INTO products (name, slug, sku, excerpt, description, price, compare_at_price, stock_quantity, stock_status, brand_id, is_active, is_featured, is_new)
VALUES
('All-Season Tire 205/55R16','all-season-tire-205-55r16','TIRE-20555R16','Quality all-season tire','Treadwear optimized',89.99, NULL, 120, 'in-stock', (SELECT id FROM brands WHERE slug='continental'), true, true, false),
('Alloy Wheel 17x7.5','alloy-wheel-17x75','WHEEL-17-ALLOY','Lightweight alloy wheel','High strength aluminum',149.50, 179.99, 45, 'in-stock', (SELECT id FROM brands WHERE slug='bosch'), true, true, true),
('Spark Plug Iridium','spark-plug-iridium','NGK-IR-01','Iridium spark plug','Long-life spark plug',8.90, NULL, 500, 'in-stock', (SELECT id FROM brands WHERE slug='ngk'), true, false, true),
('Oil Filter Premium','oil-filter-premium','DENSO-OF-10','High efficiency oil filter','10,000km interval',6.50, NULL, 350, 'in-stock', (SELECT id FROM brands WHERE slug='denso'), true, false, false),
('Brake Pads Front','brake-pads-front','GATES-BP-F','Ceramic brake pads','Low dust, quiet',39.99, 49.99, 80, 'in-stock', (SELECT id FROM brands WHERE slug='gates'), true, true, false),
('Shock Absorber Rear','shock-absorber-rear','KYB-SH-R','Gas shock absorber','Improved ride comfort',59.00, NULL, 60, 'in-stock', (SELECT id FROM brands WHERE slug='kyb'), true, false, false),
('Air Filter','air-filter','MAHLE-AF-01','Panel air filter','OEM quality',12.00, NULL, 200, 'in-stock', (SELECT id FROM brands WHERE slug='mahle'), true, false, false),
('Wiper Blade 24"','wiper-blade-24','VALEO-WB-24','All-weather wiper','Quiet performance',7.99, NULL, 400, 'in-stock', (SELECT id FROM brands WHERE slug='valeo'), true, false, true)
ON CONFLICT (slug) DO NOTHING;

-- Map products to categories
INSERT INTO product_categories (product_id, category_id, is_primary)
SELECT p.id, c.id, true FROM products p JOIN categories c ON (
    (p.slug IN ('all-season-tire-205-55r16','alloy-wheel-17x75') AND c.slug='tires-wheels') OR
    (p.slug IN ('spark-plug-iridium','oil-filter-premium','air-filter') AND c.slug='engine-drivetrain') OR
    (p.slug IN ('brake-pads-front','shock-absorber-rear') AND c.slug='interior-parts') OR
    (p.slug IN ('wiper-blade-24') AND c.slug='hand-tools')
)
ON CONFLICT DO NOTHING;

-- Optional featured/specials alignment: mark compare_at_price for discounts already set above


