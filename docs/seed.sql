-- Seed data: the 4 verified opportunities from OPZY_SOURCE_TRACKING.xlsx
-- Run this in the Supabase SQL editor after schema.sql

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
values
('Chevening Scholarship', 'UK FCDO', 'scholarship', 'Nigeria (study in UK)',
 'The UK Government''s international scholarships programme, funding a full master''s degree in the UK for future leaders.',
 '2026-10-06',
 'Nigerian nationals, minimum work experience required, must return to home country after studies',
 'https://www.chevening.org/scholarship/nigeria/', 'https://www.chevening.org/scholarship/nigeria/',
 5, true, 'active'),

('World Bank Young Professionals Program (2027 cycle)', 'World Bank Group', 'fellowship', 'Global, open to Nigerians',
 'A leadership development program for future World Bank leaders, combining rotational assignments with mentorship.',
 '2026-09-30',
 'Advanced degree required, under 32 years old, relevant professional experience',
 'https://worldbank.org/en/about/careers/programs-and-internships', 'https://worldbank.org/en/about/careers/programs-and-internships',
 5, true, 'active'),

('EBID Young Professional Programme', 'ECOWAS Bank for Investment and Development', 'fellowship', 'ECOWAS region incl. Nigeria',
 'A structured graduate program for young professionals across ECOWAS member states.',
 '2026-10-30',
 'Graduate degree, national of an ECOWAS member state',
 'https://ebid.org', 'https://ebid.org',
 4, true, 'active'),

('Wetech x Nexascale AI Hackathon', 'Wetech / Nexascale', 'hackathon', 'Lagos (in-person, AI UniPod, University of Lagos)',
 'A one-day, high-energy AI hackathon in Lagos focused on shipping practical AI solutions with diverse teams.',
 '2026-09-19',
 'Open to developers, designers, and product builders; diverse teams required',
 null, 'https://valucopglobal.com/wetech-ai-hackathon-2026-lagos-okx-africa-deep-tech-gemini-xprize-opportunities/',
 3, true, 'active');
