-- GENERATED from docs/OPZY_SOURCE_TRACKING.xlsx by backend/scripts/seed_opportunities.py.
-- Don't edit by hand: edit the sheet, then run `python -m scripts.seed_opportunities --sql`.
--
-- UNVERIFIED DATA: every row is a real opportunity, but most are still marked
-- Verified=No in the sheet (see its Notes column) pending a human confirmation pass.
-- Never run this against production until that's done.
--
-- Needs the migrated schema: run after `alembic upgrade head`.
-- Safe to re-run: rows already present (same title and organization) are updated to
-- match the sheet; unchanged rows are left alone.

update opportunities set
    title = 'Chevening Scholarship',
    organization = 'UK FCDO',
    category = 'scholarship',
    geography = 'Nigeria (study in UK)',
    description = 'The UK Government''s international scholarships programme, funding a full master''s degree in the UK for future leaders.',
    deadline = date '2026-10-06',
    eligibility_notes = 'Nigerian nationals, minimum work experience required, must return to home country after studies',
    application_url = 'https://www.chevening.org/scholarship/nigeria/',
    source_url = 'https://www.chevening.org/scholarship/nigeria/',
    quality_rating = 5,
    verified = true,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = array['graduate', 'postgraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Chevening Scholarship'
  and organization is not distinct from 'UK FCDO'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Chevening Scholarship', 'UK FCDO', 'scholarship', 'Nigeria (study in UK)', 'The UK Government''s international scholarships programme, funding a full master''s degree in the UK for future leaders.', date '2026-10-06', 'Nigerian nationals, minimum work experience required, must return to home country after studies', 'https://www.chevening.org/scholarship/nigeria/', 'https://www.chevening.org/scholarship/nigeria/', 5, true, 'active', array['NG']::text[], array['graduate', 'postgraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Chevening Scholarship',
       'UK FCDO',
       'scholarship',
       'Nigeria (study in UK)',
       'The UK Government''s international scholarships programme, funding a full master''s degree in the UK for future leaders.',
       date '2026-10-06',
       'Nigerian nationals, minimum work experience required, must return to home country after studies',
       'https://www.chevening.org/scholarship/nigeria/',
       'https://www.chevening.org/scholarship/nigeria/',
       5,
       true,
       'active',
       array['NG']::text[],
       array['graduate', 'postgraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Chevening Scholarship'
    and organization is not distinct from 'UK FCDO'
);

update opportunities set
    title = 'World Bank Young Professionals Program (2027 cycle)',
    organization = 'World Bank Group',
    category = 'fellowship',
    geography = 'Global, open to Nigerians',
    description = 'A leadership development program for future World Bank leaders, combining rotational assignments with mentorship.',
    deadline = date '2026-09-30',
    eligibility_notes = 'Advanced degree required, under 32 years old, relevant professional experience',
    application_url = 'https://worldbank.org/en/about/careers/programs-and-internships',
    source_url = 'https://worldbank.org/en/about/careers/programs-and-internships',
    quality_rating = 5,
    verified = true,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = array['postgraduate']::text[],
    fields_of_study = array['Economics', 'Finance', 'Public Health', 'Education', 'Engineering', 'Agriculture', 'Urban Planning', 'Social Sciences']::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'World Bank Young Professionals Program (2027 cycle)'
  and organization is not distinct from 'World Bank Group'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('World Bank Young Professionals Program (2027 cycle)', 'World Bank Group', 'fellowship', 'Global, open to Nigerians', 'A leadership development program for future World Bank leaders, combining rotational assignments with mentorship.', date '2026-09-30', 'Advanced degree required, under 32 years old, relevant professional experience', 'https://worldbank.org/en/about/careers/programs-and-internships', 'https://worldbank.org/en/about/careers/programs-and-internships', 5, true, 'active', '{}'::text[], array['postgraduate']::text[], array['Economics', 'Finance', 'Public Health', 'Education', 'Engineering', 'Agriculture', 'Urban Planning', 'Social Sciences']::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'World Bank Young Professionals Program (2027 cycle)',
       'World Bank Group',
       'fellowship',
       'Global, open to Nigerians',
       'A leadership development program for future World Bank leaders, combining rotational assignments with mentorship.',
       date '2026-09-30',
       'Advanced degree required, under 32 years old, relevant professional experience',
       'https://worldbank.org/en/about/careers/programs-and-internships',
       'https://worldbank.org/en/about/careers/programs-and-internships',
       5,
       true,
       'active',
       '{}'::text[],
       array['postgraduate']::text[],
       array['Economics', 'Finance', 'Public Health', 'Education', 'Engineering', 'Agriculture', 'Urban Planning', 'Social Sciences']::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'World Bank Young Professionals Program (2027 cycle)'
    and organization is not distinct from 'World Bank Group'
);

update opportunities set
    title = 'EBID Young Professional Programme',
    organization = 'ECOWAS Bank for Investment and Development',
    category = 'fellowship',
    geography = 'ECOWAS region incl. Nigeria',
    description = 'A structured graduate program for young professionals across ECOWAS member states.',
    deadline = date '2026-10-30',
    eligibility_notes = 'Graduate degree, national of an ECOWAS member state',
    application_url = 'https://ebid.org',
    source_url = 'https://ebid.org',
    quality_rating = 4,
    verified = true,
    status = 'active',
    eligible_countries = array['BJ', 'CI', 'CV', 'GH', 'GM', 'GN', 'GW', 'LR', 'NG', 'SL', 'SN', 'TG']::text[],
    education_levels = array['postgraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'EBID Young Professional Programme'
  and organization is not distinct from 'ECOWAS Bank for Investment and Development'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('EBID Young Professional Programme', 'ECOWAS Bank for Investment and Development', 'fellowship', 'ECOWAS region incl. Nigeria', 'A structured graduate program for young professionals across ECOWAS member states.', date '2026-10-30', 'Graduate degree, national of an ECOWAS member state', 'https://ebid.org', 'https://ebid.org', 4, true, 'active', array['BJ', 'CI', 'CV', 'GH', 'GM', 'GN', 'GW', 'LR', 'NG', 'SL', 'SN', 'TG']::text[], array['postgraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'EBID Young Professional Programme',
       'ECOWAS Bank for Investment and Development',
       'fellowship',
       'ECOWAS region incl. Nigeria',
       'A structured graduate program for young professionals across ECOWAS member states.',
       date '2026-10-30',
       'Graduate degree, national of an ECOWAS member state',
       'https://ebid.org',
       'https://ebid.org',
       4,
       true,
       'active',
       array['BJ', 'CI', 'CV', 'GH', 'GM', 'GN', 'GW', 'LR', 'NG', 'SL', 'SN', 'TG']::text[],
       array['postgraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'EBID Young Professional Programme'
    and organization is not distinct from 'ECOWAS Bank for Investment and Development'
);

update opportunities set
    title = 'Wetech x Nexascale AI Hackathon',
    organization = 'Wetech / Nexascale',
    category = 'hackathon',
    geography = 'Lagos (in-person, AI UniPod, University of Lagos)',
    description = 'A one-day, high-energy AI hackathon in Lagos focused on shipping practical AI solutions with diverse teams.',
    deadline = date '2026-09-19',
    eligibility_notes = 'Open to developers, designers, and product builders; diverse teams required',
    application_url = null,
    source_url = 'https://valucopglobal.com/wetech-ai-hackathon-2026-lagos-okx-africa-deep-tech-gemini-xprize-opportunities/',
    quality_rating = 3,
    verified = true,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Wetech x Nexascale AI Hackathon'
  and organization is not distinct from 'Wetech / Nexascale'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Wetech x Nexascale AI Hackathon', 'Wetech / Nexascale', 'hackathon', 'Lagos (in-person, AI UniPod, University of Lagos)', 'A one-day, high-energy AI hackathon in Lagos focused on shipping practical AI solutions with diverse teams.', date '2026-09-19', 'Open to developers, designers, and product builders; diverse teams required', null, 'https://valucopglobal.com/wetech-ai-hackathon-2026-lagos-okx-africa-deep-tech-gemini-xprize-opportunities/', 3, true, 'active', '{}'::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Wetech x Nexascale AI Hackathon',
       'Wetech / Nexascale',
       'hackathon',
       'Lagos (in-person, AI UniPod, University of Lagos)',
       'A one-day, high-energy AI hackathon in Lagos focused on shipping practical AI solutions with diverse teams.',
       date '2026-09-19',
       'Open to developers, designers, and product builders; diverse teams required',
       null,
       'https://valucopglobal.com/wetech-ai-hackathon-2026-lagos-okx-africa-deep-tech-gemini-xprize-opportunities/',
       3,
       true,
       'active',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Wetech x Nexascale AI Hackathon'
    and organization is not distinct from 'Wetech / Nexascale'
);

update opportunities set
    title = 'Commonwealth Master''s Scholarships 2027/2028',
    organization = 'UK Foreign, Commonwealth & Development Office (FCDO)',
    category = 'scholarship',
    geography = 'Nigeria (study in UK)',
    description = 'Fully funded master''s scholarships in the UK for citizens of eligible developing Commonwealth countries, administered by the Commonwealth Scholarship Commission.',
    deadline = date '2026-10-20',
    eligibility_notes = 'Nigerian nationals from eligible developing Commonwealth countries; must return home after studies; typically requires a first-class or strong second-class degree.',
    application_url = 'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-masters-scholarships',
    source_url = 'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-masters-scholarships',
    quality_rating = 5,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = array['graduate', 'postgraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Commonwealth Master''s Scholarships 2027/2028'
  and organization is not distinct from 'UK Foreign, Commonwealth & Development Office (FCDO)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Commonwealth Master''s Scholarships 2027/2028', 'UK Foreign, Commonwealth & Development Office (FCDO)', 'scholarship', 'Nigeria (study in UK)', 'Fully funded master''s scholarships in the UK for citizens of eligible developing Commonwealth countries, administered by the Commonwealth Scholarship Commission.', date '2026-10-20', 'Nigerian nationals from eligible developing Commonwealth countries; must return home after studies; typically requires a first-class or strong second-class degree.', 'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-masters-scholarships', 'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-masters-scholarships', 5, false, 'active', array['NG']::text[], array['graduate', 'postgraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Commonwealth Master''s Scholarships 2027/2028',
       'UK Foreign, Commonwealth & Development Office (FCDO)',
       'scholarship',
       'Nigeria (study in UK)',
       'Fully funded master''s scholarships in the UK for citizens of eligible developing Commonwealth countries, administered by the Commonwealth Scholarship Commission.',
       date '2026-10-20',
       'Nigerian nationals from eligible developing Commonwealth countries; must return home after studies; typically requires a first-class or strong second-class degree.',
       'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-masters-scholarships',
       'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-masters-scholarships',
       5,
       false,
       'active',
       array['NG']::text[],
       array['graduate', 'postgraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Commonwealth Master''s Scholarships 2027/2028'
    and organization is not distinct from 'UK Foreign, Commonwealth & Development Office (FCDO)'
);

update opportunities set
    title = 'Commonwealth PhD Scholarships 2027/2028',
    organization = 'UK Foreign, Commonwealth & Development Office (FCDO)',
    category = 'scholarship',
    geography = 'Nigeria (study in UK)',
    description = 'Fully funded doctoral scholarships in the UK for talented individuals from developing Commonwealth countries who could not otherwise afford to study in the UK.',
    deadline = date '2026-10-20',
    eligibility_notes = 'Nigerian nationals; eligibility route and funding vary by scholarship category.',
    application_url = 'https://cscuk.fcdo.gov.uk/scholarships/',
    source_url = 'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-phd-scholarships-for-least-developed-countries-and-vulnerable-states',
    quality_rating = 4,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = array['postgraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Commonwealth PhD Scholarships 2027/2028'
  and organization is not distinct from 'UK Foreign, Commonwealth & Development Office (FCDO)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Commonwealth PhD Scholarships 2027/2028', 'UK Foreign, Commonwealth & Development Office (FCDO)', 'scholarship', 'Nigeria (study in UK)', 'Fully funded doctoral scholarships in the UK for talented individuals from developing Commonwealth countries who could not otherwise afford to study in the UK.', date '2026-10-20', 'Nigerian nationals; eligibility route and funding vary by scholarship category.', 'https://cscuk.fcdo.gov.uk/scholarships/', 'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-phd-scholarships-for-least-developed-countries-and-vulnerable-states', 4, false, 'active', array['NG']::text[], array['postgraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Commonwealth PhD Scholarships 2027/2028',
       'UK Foreign, Commonwealth & Development Office (FCDO)',
       'scholarship',
       'Nigeria (study in UK)',
       'Fully funded doctoral scholarships in the UK for talented individuals from developing Commonwealth countries who could not otherwise afford to study in the UK.',
       date '2026-10-20',
       'Nigerian nationals; eligibility route and funding vary by scholarship category.',
       'https://cscuk.fcdo.gov.uk/scholarships/',
       'https://cscuk.fcdo.gov.uk/scholarships/commonwealth-phd-scholarships-for-least-developed-countries-and-vulnerable-states',
       4,
       false,
       'active',
       array['NG']::text[],
       array['postgraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Commonwealth PhD Scholarships 2027/2028'
    and organization is not distinct from 'UK Foreign, Commonwealth & Development Office (FCDO)'
);

update opportunities set
    title = 'Gates Cambridge Scholarship 2027/2028',
    organization = 'Gates Cambridge Trust / University of Cambridge',
    category = 'scholarship',
    geography = 'Nigeria (study in UK)',
    description = 'Full-cost postgraduate scholarship at the University of Cambridge for outstanding applicants from outside the UK, in any subject.',
    deadline = date '2026-10-14',
    eligibility_notes = 'Non-UK citizens applying for a full-time postgraduate course at Cambridge; outstanding academic record and leadership potential.',
    application_url = 'https://www.gatescambridge.org/apply/',
    source_url = 'https://www.gatescambridge.org/apply/',
    quality_rating = 5,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = array['postgraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Gates Cambridge Scholarship 2027/2028'
  and organization is not distinct from 'Gates Cambridge Trust / University of Cambridge'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Gates Cambridge Scholarship 2027/2028', 'Gates Cambridge Trust / University of Cambridge', 'scholarship', 'Nigeria (study in UK)', 'Full-cost postgraduate scholarship at the University of Cambridge for outstanding applicants from outside the UK, in any subject.', date '2026-10-14', 'Non-UK citizens applying for a full-time postgraduate course at Cambridge; outstanding academic record and leadership potential.', 'https://www.gatescambridge.org/apply/', 'https://www.gatescambridge.org/apply/', 5, false, 'active', '{}'::text[], array['postgraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Gates Cambridge Scholarship 2027/2028',
       'Gates Cambridge Trust / University of Cambridge',
       'scholarship',
       'Nigeria (study in UK)',
       'Full-cost postgraduate scholarship at the University of Cambridge for outstanding applicants from outside the UK, in any subject.',
       date '2026-10-14',
       'Non-UK citizens applying for a full-time postgraduate course at Cambridge; outstanding academic record and leadership potential.',
       'https://www.gatescambridge.org/apply/',
       'https://www.gatescambridge.org/apply/',
       5,
       false,
       'active',
       '{}'::text[],
       array['postgraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Gates Cambridge Scholarship 2027/2028'
    and organization is not distinct from 'Gates Cambridge Trust / University of Cambridge'
);

update opportunities set
    title = 'Mastercard Foundation AfOx Graduate Scholarships 2027/2028',
    organization = 'Mastercard Foundation / African Oxford Initiative (AfOx), University of Oxford',
    category = 'scholarship',
    geography = 'Nigeria (study in UK)',
    description = 'Fully funded graduate scholarships at the University of Oxford for African citizens resident in Africa, part of the Mastercard Foundation Scholars Program.',
    deadline = date '2027-01-06',
    eligibility_notes = 'African citizens resident in an African country; demonstrated financial need and leadership potential.',
    application_url = 'https://www.law.ox.ac.uk/mastercard-foundation-afox-scholarships',
    source_url = 'https://www.law.ox.ac.uk/mastercard-foundation-afox-scholarships',
    quality_rating = 4,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = array['postgraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Mastercard Foundation AfOx Graduate Scholarships 2027/2028'
  and organization is not distinct from 'Mastercard Foundation / African Oxford Initiative (AfOx), University of Oxford'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Mastercard Foundation AfOx Graduate Scholarships 2027/2028', 'Mastercard Foundation / African Oxford Initiative (AfOx), University of Oxford', 'scholarship', 'Nigeria (study in UK)', 'Fully funded graduate scholarships at the University of Oxford for African citizens resident in Africa, part of the Mastercard Foundation Scholars Program.', date '2027-01-06', 'African citizens resident in an African country; demonstrated financial need and leadership potential.', 'https://www.law.ox.ac.uk/mastercard-foundation-afox-scholarships', 'https://www.law.ox.ac.uk/mastercard-foundation-afox-scholarships', 4, false, 'active', '{}'::text[], array['postgraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Mastercard Foundation AfOx Graduate Scholarships 2027/2028',
       'Mastercard Foundation / African Oxford Initiative (AfOx), University of Oxford',
       'scholarship',
       'Nigeria (study in UK)',
       'Fully funded graduate scholarships at the University of Oxford for African citizens resident in Africa, part of the Mastercard Foundation Scholars Program.',
       date '2027-01-06',
       'African citizens resident in an African country; demonstrated financial need and leadership potential.',
       'https://www.law.ox.ac.uk/mastercard-foundation-afox-scholarships',
       'https://www.law.ox.ac.uk/mastercard-foundation-afox-scholarships',
       4,
       false,
       'active',
       '{}'::text[],
       array['postgraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Mastercard Foundation AfOx Graduate Scholarships 2027/2028'
    and organization is not distinct from 'Mastercard Foundation / African Oxford Initiative (AfOx), University of Oxford'
);

update opportunities set
    title = 'Mandela Washington Fellowship (YALI) 2027',
    organization = 'U.S. Department of State / Young African Leaders Initiative (YALI)',
    category = 'fellowship',
    geography = 'Nigeria (6-week program in the USA)',
    description = 'Flagship YALI program: a six-week leadership institute at a U.S. university, followed by a summit in Washington, DC, for young African leaders in business, civic engagement, or public management.',
    deadline = date '2026-10-13',
    eligibility_notes = 'Age 25-35 by Oct 13 2026 (exceptional 21-24 year olds considered); citizen and resident of an eligible Sub-Saharan African country, including Nigeria.',
    application_url = 'https://www.mandelawashingtonfellowship.org/',
    source_url = 'https://www.mandelawashingtonfellowship.org/',
    quality_rating = 5,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Mandela Washington Fellowship (YALI) 2027'
  and organization is not distinct from 'U.S. Department of State / Young African Leaders Initiative (YALI)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Mandela Washington Fellowship (YALI) 2027', 'U.S. Department of State / Young African Leaders Initiative (YALI)', 'fellowship', 'Nigeria (6-week program in the USA)', 'Flagship YALI program: a six-week leadership institute at a U.S. university, followed by a summit in Washington, DC, for young African leaders in business, civic engagement, or public management.', date '2026-10-13', 'Age 25-35 by Oct 13 2026 (exceptional 21-24 year olds considered); citizen and resident of an eligible Sub-Saharan African country, including Nigeria.', 'https://www.mandelawashingtonfellowship.org/', 'https://www.mandelawashingtonfellowship.org/', 5, false, 'active', array['NG']::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Mandela Washington Fellowship (YALI) 2027',
       'U.S. Department of State / Young African Leaders Initiative (YALI)',
       'fellowship',
       'Nigeria (6-week program in the USA)',
       'Flagship YALI program: a six-week leadership institute at a U.S. university, followed by a summit in Washington, DC, for young African leaders in business, civic engagement, or public management.',
       date '2026-10-13',
       'Age 25-35 by Oct 13 2026 (exceptional 21-24 year olds considered); citizen and resident of an eligible Sub-Saharan African country, including Nigeria.',
       'https://www.mandelawashingtonfellowship.org/',
       'https://www.mandelawashingtonfellowship.org/',
       5,
       false,
       'active',
       array['NG']::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Mandela Washington Fellowship (YALI) 2027'
    and organization is not distinct from 'U.S. Department of State / Young African Leaders Initiative (YALI)'
);

update opportunities set
    title = 'Anzisha Fellowship 2027',
    organization = 'Anzisha Prize (African Leadership Academy & Mastercard Foundation)',
    category = 'fellowship',
    geography = 'Nigeria (pan-African)',
    description = 'Multi-year venture-building fellowship for very young African entrepreneurs already running a real business, with mentorship, grants, and business support.',
    deadline = date '2026-11-10',
    eligibility_notes = 'Age 15-22, citizen of an African country, founding member of an already-operating business with real customers or revenue — an idea alone does not qualify.',
    application_url = 'https://anzisha.org/apply/',
    source_url = 'https://anzisha.org/apply/',
    quality_rating = 5,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Anzisha Fellowship 2027'
  and organization is not distinct from 'Anzisha Prize (African Leadership Academy & Mastercard Foundation)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Anzisha Fellowship 2027', 'Anzisha Prize (African Leadership Academy & Mastercard Foundation)', 'fellowship', 'Nigeria (pan-African)', 'Multi-year venture-building fellowship for very young African entrepreneurs already running a real business, with mentorship, grants, and business support.', date '2026-11-10', 'Age 15-22, citizen of an African country, founding member of an already-operating business with real customers or revenue — an idea alone does not qualify.', 'https://anzisha.org/apply/', 'https://anzisha.org/apply/', 5, false, 'active', '{}'::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Anzisha Fellowship 2027',
       'Anzisha Prize (African Leadership Academy & Mastercard Foundation)',
       'fellowship',
       'Nigeria (pan-African)',
       'Multi-year venture-building fellowship for very young African entrepreneurs already running a real business, with mentorship, grants, and business support.',
       date '2026-11-10',
       'Age 15-22, citizen of an African country, founding member of an already-operating business with real customers or revenue — an idea alone does not qualify.',
       'https://anzisha.org/apply/',
       'https://anzisha.org/apply/',
       5,
       false,
       'active',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Anzisha Fellowship 2027'
    and organization is not distinct from 'Anzisha Prize (African Leadership Academy & Mastercard Foundation)'
);

update opportunities set
    title = 'She Leads Africa BoostHer Program 2026',
    organization = 'She Leads Africa (SLA)',
    category = 'fellowship',
    geography = 'Nigeria',
    description = 'Career-readiness and mentorship program for young Nigerian women — students, undergraduates, and recent graduates — with expert-led training, mentorship, and access to job/business opportunities.',
    deadline = null::date,
    eligibility_notes = 'Nigerian women aged 18-35.',
    application_url = 'https://sheleadsafrica.org/boostherform/',
    source_url = 'https://opportunitydesk.org/2026/08/25/sla-boosther-program-2026/',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'She Leads Africa BoostHer Program 2026'
  and organization is not distinct from 'She Leads Africa (SLA)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('She Leads Africa BoostHer Program 2026', 'She Leads Africa (SLA)', 'fellowship', 'Nigeria', 'Career-readiness and mentorship program for young Nigerian women — students, undergraduates, and recent graduates — with expert-led training, mentorship, and access to job/business opportunities.', null::date, 'Nigerian women aged 18-35.', 'https://sheleadsafrica.org/boostherform/', 'https://opportunitydesk.org/2026/08/25/sla-boosther-program-2026/', 3, false, 'active', array['NG']::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'She Leads Africa BoostHer Program 2026',
       'She Leads Africa (SLA)',
       'fellowship',
       'Nigeria',
       'Career-readiness and mentorship program for young Nigerian women — students, undergraduates, and recent graduates — with expert-led training, mentorship, and access to job/business opportunities.',
       null::date,
       'Nigerian women aged 18-35.',
       'https://sheleadsafrica.org/boostherform/',
       'https://opportunitydesk.org/2026/08/25/sla-boosther-program-2026/',
       3,
       false,
       'active',
       array['NG']::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'She Leads Africa BoostHer Program 2026'
    and organization is not distinct from 'She Leads Africa (SLA)'
);

update opportunities set
    title = 'Yenching Academy at Peking University 2027',
    organization = 'Peking University',
    category = 'scholarship',
    geography = 'Nigeria (study in China)',
    description = 'Fully funded one-year interdisciplinary master''s program in China Studies at Peking University for international applicants with strong academic records.',
    deadline = date '2026-11-30',
    eligibility_notes = 'International applicants with a bachelor''s degree; open to all nationalities, including Nigeria.',
    application_url = 'https://yenchingacademy.pku.edu.cn/',
    source_url = 'https://yenchingacademy.pku.edu.cn/',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = array['postgraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Yenching Academy at Peking University 2027'
  and organization is not distinct from 'Peking University'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Yenching Academy at Peking University 2027', 'Peking University', 'scholarship', 'Nigeria (study in China)', 'Fully funded one-year interdisciplinary master''s program in China Studies at Peking University for international applicants with strong academic records.', date '2026-11-30', 'International applicants with a bachelor''s degree; open to all nationalities, including Nigeria.', 'https://yenchingacademy.pku.edu.cn/', 'https://yenchingacademy.pku.edu.cn/', 3, false, 'active', '{}'::text[], array['postgraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Yenching Academy at Peking University 2027',
       'Peking University',
       'scholarship',
       'Nigeria (study in China)',
       'Fully funded one-year interdisciplinary master''s program in China Studies at Peking University for international applicants with strong academic records.',
       date '2026-11-30',
       'International applicants with a bachelor''s degree; open to all nationalities, including Nigeria.',
       'https://yenchingacademy.pku.edu.cn/',
       'https://yenchingacademy.pku.edu.cn/',
       3,
       false,
       'active',
       '{}'::text[],
       array['postgraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Yenching Academy at Peking University 2027'
    and organization is not distinct from 'Peking University'
);

update opportunities set
    title = 'One Young World Summit 2026 Scholarship',
    organization = 'One Young World',
    category = 'fellowship',
    geography = 'Nigeria (summit in Cape Town, South Africa)',
    description = 'Fully funded scholarship to attend the One Young World Summit in Cape Town — a global gathering of young leaders aged 18-35 from underrepresented countries working on social impact.',
    deadline = date '2026-10-31',
    eligibility_notes = 'Age 18-35, from underrepresented countries including Nigeria, with demonstrated leadership or impact work.',
    application_url = 'https://www.oneyoungworld.com/scholarships',
    source_url = 'https://www.oneyoungworld.com/scholarships',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'One Young World Summit 2026 Scholarship'
  and organization is not distinct from 'One Young World'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('One Young World Summit 2026 Scholarship', 'One Young World', 'fellowship', 'Nigeria (summit in Cape Town, South Africa)', 'Fully funded scholarship to attend the One Young World Summit in Cape Town — a global gathering of young leaders aged 18-35 from underrepresented countries working on social impact.', date '2026-10-31', 'Age 18-35, from underrepresented countries including Nigeria, with demonstrated leadership or impact work.', 'https://www.oneyoungworld.com/scholarships', 'https://www.oneyoungworld.com/scholarships', 3, false, 'active', '{}'::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'One Young World Summit 2026 Scholarship',
       'One Young World',
       'fellowship',
       'Nigeria (summit in Cape Town, South Africa)',
       'Fully funded scholarship to attend the One Young World Summit in Cape Town — a global gathering of young leaders aged 18-35 from underrepresented countries working on social impact.',
       date '2026-10-31',
       'Age 18-35, from underrepresented countries including Nigeria, with demonstrated leadership or impact work.',
       'https://www.oneyoungworld.com/scholarships',
       'https://www.oneyoungworld.com/scholarships',
       3,
       false,
       'active',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'One Young World Summit 2026 Scholarship'
    and organization is not distinct from 'One Young World'
);

update opportunities set
    title = 'Global Entrepreneurship Festival — Entrepreneurs Investment Program (EIP) 2026',
    organization = 'Global Entrepreneurship Festival',
    category = 'grant',
    geography = 'Nigeria (global program)',
    description = 'Entrepreneurs Investment Program offering up to $35,000 in total seed investment for founders at any stage with an innovative business idea.',
    deadline = date '2026-10-06',
    eligibility_notes = 'Founders of any nationality and startup stage; full criteria on the official site.',
    application_url = 'https://www.globalentrepreneurshipfestival.com/eip',
    source_url = 'https://www.globalentrepreneurshipfestival.com/eip',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Global Entrepreneurship Festival — Entrepreneurs Investment Program (EIP) 2026'
  and organization is not distinct from 'Global Entrepreneurship Festival'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Global Entrepreneurship Festival — Entrepreneurs Investment Program (EIP) 2026', 'Global Entrepreneurship Festival', 'grant', 'Nigeria (global program)', 'Entrepreneurs Investment Program offering up to $35,000 in total seed investment for founders at any stage with an innovative business idea.', date '2026-10-06', 'Founders of any nationality and startup stage; full criteria on the official site.', 'https://www.globalentrepreneurshipfestival.com/eip', 'https://www.globalentrepreneurshipfestival.com/eip', 3, false, 'active', '{}'::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Global Entrepreneurship Festival — Entrepreneurs Investment Program (EIP) 2026',
       'Global Entrepreneurship Festival',
       'grant',
       'Nigeria (global program)',
       'Entrepreneurs Investment Program offering up to $35,000 in total seed investment for founders at any stage with an innovative business idea.',
       date '2026-10-06',
       'Founders of any nationality and startup stage; full criteria on the official site.',
       'https://www.globalentrepreneurshipfestival.com/eip',
       'https://www.globalentrepreneurshipfestival.com/eip',
       3,
       false,
       'active',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Global Entrepreneurship Festival — Entrepreneurs Investment Program (EIP) 2026'
    and organization is not distinct from 'Global Entrepreneurship Festival'
);

update opportunities set
    title = 'AGNES Intra-Africa Mobility Grants 2026',
    organization = 'African Germany Network of Excellence in Science (AGNES)',
    category = 'grant',
    geography = 'Nigeria (pan-Sub-Saharan Africa)',
    description = 'Research mobility grants (EUR 2,300-3,000) for junior/doctoral researchers in sub-Saharan Africa to build research networks and mentorship across the continent.',
    deadline = date '2026-10-16',
    eligibility_notes = 'Registered doctoral researchers based in sub-Saharan Africa.',
    application_url = 'https://agnes-h.org/2026-agnes-intra-africa-mobility-grants-for-junior-researchers/',
    source_url = 'https://agnes-h.org/2026-agnes-intra-africa-mobility-grants-for-junior-researchers/',
    quality_rating = 2,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = array['postgraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'AGNES Intra-Africa Mobility Grants 2026'
  and organization is not distinct from 'African Germany Network of Excellence in Science (AGNES)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('AGNES Intra-Africa Mobility Grants 2026', 'African Germany Network of Excellence in Science (AGNES)', 'grant', 'Nigeria (pan-Sub-Saharan Africa)', 'Research mobility grants (EUR 2,300-3,000) for junior/doctoral researchers in sub-Saharan Africa to build research networks and mentorship across the continent.', date '2026-10-16', 'Registered doctoral researchers based in sub-Saharan Africa.', 'https://agnes-h.org/2026-agnes-intra-africa-mobility-grants-for-junior-researchers/', 'https://agnes-h.org/2026-agnes-intra-africa-mobility-grants-for-junior-researchers/', 2, false, 'active', '{}'::text[], array['postgraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'AGNES Intra-Africa Mobility Grants 2026',
       'African Germany Network of Excellence in Science (AGNES)',
       'grant',
       'Nigeria (pan-Sub-Saharan Africa)',
       'Research mobility grants (EUR 2,300-3,000) for junior/doctoral researchers in sub-Saharan Africa to build research networks and mentorship across the continent.',
       date '2026-10-16',
       'Registered doctoral researchers based in sub-Saharan Africa.',
       'https://agnes-h.org/2026-agnes-intra-africa-mobility-grants-for-junior-researchers/',
       'https://agnes-h.org/2026-agnes-intra-africa-mobility-grants-for-junior-researchers/',
       2,
       false,
       'active',
       '{}'::text[],
       array['postgraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'AGNES Intra-Africa Mobility Grants 2026'
    and organization is not distinct from 'African Germany Network of Excellence in Science (AGNES)'
);

update opportunities set
    title = 'D-Prize Global Competition 2026',
    organization = 'D-Prize',
    category = 'competition',
    geography = 'Nigeria (global, low/middle-income countries)',
    description = 'Global competition awarding up to $20,000 to entrepreneurs launching new organizations that distribute proven poverty interventions in low- and middle-income countries.',
    deadline = date '2026-12-06',
    eligibility_notes = 'Open to anyone proposing to launch a new venture distributing a proven intervention in a low/middle-income country, including Nigeria.',
    application_url = 'https://www.dprize.org/',
    source_url = 'https://www.dprize.org/',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'D-Prize Global Competition 2026'
  and organization is not distinct from 'D-Prize'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('D-Prize Global Competition 2026', 'D-Prize', 'competition', 'Nigeria (global, low/middle-income countries)', 'Global competition awarding up to $20,000 to entrepreneurs launching new organizations that distribute proven poverty interventions in low- and middle-income countries.', date '2026-12-06', 'Open to anyone proposing to launch a new venture distributing a proven intervention in a low/middle-income country, including Nigeria.', 'https://www.dprize.org/', 'https://www.dprize.org/', 3, false, 'active', '{}'::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'D-Prize Global Competition 2026',
       'D-Prize',
       'competition',
       'Nigeria (global, low/middle-income countries)',
       'Global competition awarding up to $20,000 to entrepreneurs launching new organizations that distribute proven poverty interventions in low- and middle-income countries.',
       date '2026-12-06',
       'Open to anyone proposing to launch a new venture distributing a proven intervention in a low/middle-income country, including Nigeria.',
       'https://www.dprize.org/',
       'https://www.dprize.org/',
       3,
       false,
       'active',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'D-Prize Global Competition 2026'
    and organization is not distinct from 'D-Prize'
);

update opportunities set
    title = 'Ashoka Carnegie Challenge for Civic Leadership 2027',
    organization = 'Ashoka',
    category = 'competition',
    geography = 'Nigeria',
    description = 'Challenge for young changemakers (age 20 and under) in Kenya, Nigeria, South Africa, and the USA leading civic initiatives in their schools and communities, offering seed grants and recognition.',
    deadline = date '2027-01-31',
    eligibility_notes = 'Age 20 and under; based in Kenya, Nigeria, South Africa, or USA.',
    application_url = 'https://www.ashoka.org/',
    source_url = 'https://www.ashoka.org/',
    quality_rating = 2,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = array['secondary', 'undergraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Ashoka Carnegie Challenge for Civic Leadership 2027'
  and organization is not distinct from 'Ashoka'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Ashoka Carnegie Challenge for Civic Leadership 2027', 'Ashoka', 'competition', 'Nigeria', 'Challenge for young changemakers (age 20 and under) in Kenya, Nigeria, South Africa, and the USA leading civic initiatives in their schools and communities, offering seed grants and recognition.', date '2027-01-31', 'Age 20 and under; based in Kenya, Nigeria, South Africa, or USA.', 'https://www.ashoka.org/', 'https://www.ashoka.org/', 2, false, 'active', array['NG']::text[], array['secondary', 'undergraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Ashoka Carnegie Challenge for Civic Leadership 2027',
       'Ashoka',
       'competition',
       'Nigeria',
       'Challenge for young changemakers (age 20 and under) in Kenya, Nigeria, South Africa, and the USA leading civic initiatives in their schools and communities, offering seed grants and recognition.',
       date '2027-01-31',
       'Age 20 and under; based in Kenya, Nigeria, South Africa, or USA.',
       'https://www.ashoka.org/',
       'https://www.ashoka.org/',
       2,
       false,
       'active',
       array['NG']::text[],
       array['secondary', 'undergraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Ashoka Carnegie Challenge for Civic Leadership 2027'
    and organization is not distinct from 'Ashoka'
);

update opportunities set
    title = 'InnovateX 2026',
    organization = 'Ecobank',
    category = 'hackathon',
    geography = 'Nigeria',
    description = 'Ecobank''s flagship innovation challenge for young Nigerians aged 16-30, with two tracks (Inclusive Finance, Creative Economy) and a NGN 20 million total prize pool across a six-week competition.',
    deadline = date '2026-10-30',
    eligibility_notes = 'Nigerian citizens aged 16-30, preferably tertiary students, teams of exactly 4.',
    application_url = 'https://www.innovatex.africa/',
    source_url = 'https://www.innovatex.africa/',
    quality_rating = 4,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'InnovateX 2026'
  and organization is not distinct from 'Ecobank'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('InnovateX 2026', 'Ecobank', 'hackathon', 'Nigeria', 'Ecobank''s flagship innovation challenge for young Nigerians aged 16-30, with two tracks (Inclusive Finance, Creative Economy) and a NGN 20 million total prize pool across a six-week competition.', date '2026-10-30', 'Nigerian citizens aged 16-30, preferably tertiary students, teams of exactly 4.', 'https://www.innovatex.africa/', 'https://www.innovatex.africa/', 4, false, 'active', array['NG']::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'InnovateX 2026',
       'Ecobank',
       'hackathon',
       'Nigeria',
       'Ecobank''s flagship innovation challenge for young Nigerians aged 16-30, with two tracks (Inclusive Finance, Creative Economy) and a NGN 20 million total prize pool across a six-week competition.',
       date '2026-10-30',
       'Nigerian citizens aged 16-30, preferably tertiary students, teams of exactly 4.',
       'https://www.innovatex.africa/',
       'https://www.innovatex.africa/',
       4,
       false,
       'active',
       array['NG']::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'InnovateX 2026'
    and organization is not distinct from 'Ecobank'
);

update opportunities set
    title = 'GTCO Squad Hackathon 2026',
    organization = 'Guaranty Trust Holding Company (GTCO) / HabariPay',
    category = 'hackathon',
    geography = 'Nigeria',
    description = 'Fintech/AI hackathon themed "Smart Systems: The Intelligent Economy" for Nigerian university students, with up to NGN 10 million in prizes.',
    deadline = null::date,
    eligibility_notes = 'University students in Nigeria, teams of 2-4 with at least one technical member, valid student ID.',
    application_url = 'https://squadco.com/hackathon/',
    source_url = 'https://msmeafricaonline.com/call-for-applications-gtco-squad-hackathon-program-2026-for-nigerians-up-to-%E2%82%A610-million-in-prizes/',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = array['undergraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'GTCO Squad Hackathon 2026'
  and organization is not distinct from 'Guaranty Trust Holding Company (GTCO) / HabariPay'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('GTCO Squad Hackathon 2026', 'Guaranty Trust Holding Company (GTCO) / HabariPay', 'hackathon', 'Nigeria', 'Fintech/AI hackathon themed "Smart Systems: The Intelligent Economy" for Nigerian university students, with up to NGN 10 million in prizes.', null::date, 'University students in Nigeria, teams of 2-4 with at least one technical member, valid student ID.', 'https://squadco.com/hackathon/', 'https://msmeafricaonline.com/call-for-applications-gtco-squad-hackathon-program-2026-for-nigerians-up-to-%E2%82%A610-million-in-prizes/', 3, false, 'active', array['NG']::text[], array['undergraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'GTCO Squad Hackathon 2026',
       'Guaranty Trust Holding Company (GTCO) / HabariPay',
       'hackathon',
       'Nigeria',
       'Fintech/AI hackathon themed "Smart Systems: The Intelligent Economy" for Nigerian university students, with up to NGN 10 million in prizes.',
       null::date,
       'University students in Nigeria, teams of 2-4 with at least one technical member, valid student ID.',
       'https://squadco.com/hackathon/',
       'https://msmeafricaonline.com/call-for-applications-gtco-squad-hackathon-program-2026-for-nigerians-up-to-%E2%82%A610-million-in-prizes/',
       3,
       false,
       'active',
       array['NG']::text[],
       array['undergraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'GTCO Squad Hackathon 2026'
    and organization is not distinct from 'Guaranty Trust Holding Company (GTCO) / HabariPay'
);

update opportunities set
    title = 'DevFest Lagos 2026',
    organization = 'Google Developer Groups (GDG) Lagos',
    category = 'hackathon',
    geography = 'Nigeria',
    description = '14th edition of DevFest Lagos, a large GDG-run tech conference with 4+ tracks (AI/ML, cloud, web, mobile, design, cybersecurity).',
    deadline = date '2026-11-13',
    eligibility_notes = 'Open to all; paid tickets from NGN 8,000.',
    application_url = 'https://devfestlagos.com/',
    source_url = 'https://devfestlagos.com/',
    quality_rating = 2,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'DevFest Lagos 2026'
  and organization is not distinct from 'Google Developer Groups (GDG) Lagos'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('DevFest Lagos 2026', 'Google Developer Groups (GDG) Lagos', 'hackathon', 'Nigeria', '14th edition of DevFest Lagos, a large GDG-run tech conference with 4+ tracks (AI/ML, cloud, web, mobile, design, cybersecurity).', date '2026-11-13', 'Open to all; paid tickets from NGN 8,000.', 'https://devfestlagos.com/', 'https://devfestlagos.com/', 2, false, 'active', array['NG']::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'DevFest Lagos 2026',
       'Google Developer Groups (GDG) Lagos',
       'hackathon',
       'Nigeria',
       '14th edition of DevFest Lagos, a large GDG-run tech conference with 4+ tracks (AI/ML, cloud, web, mobile, design, cybersecurity).',
       date '2026-11-13',
       'Open to all; paid tickets from NGN 8,000.',
       'https://devfestlagos.com/',
       'https://devfestlagos.com/',
       2,
       false,
       'active',
       array['NG']::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'DevFest Lagos 2026'
    and organization is not distinct from 'Google Developer Groups (GDG) Lagos'
);

update opportunities set
    title = 'Flutterwave — Frontend Engineer (Lekki)',
    organization = 'Flutterwave',
    category = 'job',
    geography = 'Nigeria (Lekki, Lagos)',
    description = 'Frontend Engineer role at Flutterwave, a leading African fintech payments company.',
    deadline = null::date,
    eligibility_notes = null,
    application_url = 'https://www.flutterwave.com/ng/careers',
    source_url = 'https://ng.indeed.com/cmp/Flutterwave',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Flutterwave — Frontend Engineer (Lekki)'
  and organization is not distinct from 'Flutterwave'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Flutterwave — Frontend Engineer (Lekki)', 'Flutterwave', 'job', 'Nigeria (Lekki, Lagos)', 'Frontend Engineer role at Flutterwave, a leading African fintech payments company.', null::date, null, 'https://www.flutterwave.com/ng/careers', 'https://ng.indeed.com/cmp/Flutterwave', 3, false, 'active', '{}'::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Flutterwave — Frontend Engineer (Lekki)',
       'Flutterwave',
       'job',
       'Nigeria (Lekki, Lagos)',
       'Frontend Engineer role at Flutterwave, a leading African fintech payments company.',
       null::date,
       null,
       'https://www.flutterwave.com/ng/careers',
       'https://ng.indeed.com/cmp/Flutterwave',
       3,
       false,
       'active',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Flutterwave — Frontend Engineer (Lekki)'
    and organization is not distinct from 'Flutterwave'
);

update opportunities set
    title = 'Flutterwave — Product Manager (Lekki)',
    organization = 'Flutterwave',
    category = 'job',
    geography = 'Nigeria (Lekki, Lagos)',
    description = 'Product Manager role at Flutterwave, a leading African fintech payments company.',
    deadline = null::date,
    eligibility_notes = null,
    application_url = 'https://www.flutterwave.com/ng/careers',
    source_url = 'https://ng.indeed.com/cmp/Flutterwave',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Flutterwave — Product Manager (Lekki)'
  and organization is not distinct from 'Flutterwave'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Flutterwave — Product Manager (Lekki)', 'Flutterwave', 'job', 'Nigeria (Lekki, Lagos)', 'Product Manager role at Flutterwave, a leading African fintech payments company.', null::date, null, 'https://www.flutterwave.com/ng/careers', 'https://ng.indeed.com/cmp/Flutterwave', 3, false, 'active', '{}'::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Flutterwave — Product Manager (Lekki)',
       'Flutterwave',
       'job',
       'Nigeria (Lekki, Lagos)',
       'Product Manager role at Flutterwave, a leading African fintech payments company.',
       null::date,
       null,
       'https://www.flutterwave.com/ng/careers',
       'https://ng.indeed.com/cmp/Flutterwave',
       3,
       false,
       'active',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Flutterwave — Product Manager (Lekki)'
    and organization is not distinct from 'Flutterwave'
);

update opportunities set
    title = 'Paystack — Senior Brand Designer (Lagos)',
    organization = 'Paystack',
    category = 'job',
    geography = 'Nigeria (Lagos)',
    description = 'Senior Brand Designer role at Paystack, a leading Nigerian fintech payments company.',
    deadline = null::date,
    eligibility_notes = null,
    application_url = 'https://paystack.com/careers',
    source_url = 'https://ng.indeed.com/cmp/Paystack',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Paystack — Senior Brand Designer (Lagos)'
  and organization is not distinct from 'Paystack'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Paystack — Senior Brand Designer (Lagos)', 'Paystack', 'job', 'Nigeria (Lagos)', 'Senior Brand Designer role at Paystack, a leading Nigerian fintech payments company.', null::date, null, 'https://paystack.com/careers', 'https://ng.indeed.com/cmp/Paystack', 3, false, 'active', '{}'::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Paystack — Senior Brand Designer (Lagos)',
       'Paystack',
       'job',
       'Nigeria (Lagos)',
       'Senior Brand Designer role at Paystack, a leading Nigerian fintech payments company.',
       null::date,
       null,
       'https://paystack.com/careers',
       'https://ng.indeed.com/cmp/Paystack',
       3,
       false,
       'active',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Paystack — Senior Brand Designer (Lagos)'
    and organization is not distinct from 'Paystack'
);

update opportunities set
    title = 'Paystack — Senior Backend Engineer (Abuja)',
    organization = 'Paystack',
    category = 'job',
    geography = 'Nigeria (Abuja)',
    description = 'Senior Backend Engineer role at Paystack, a leading Nigerian fintech payments company.',
    deadline = null::date,
    eligibility_notes = null,
    application_url = 'https://paystack.com/careers',
    source_url = 'https://ng.indeed.com/cmp/Paystack',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Paystack — Senior Backend Engineer (Abuja)'
  and organization is not distinct from 'Paystack'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Paystack — Senior Backend Engineer (Abuja)', 'Paystack', 'job', 'Nigeria (Abuja)', 'Senior Backend Engineer role at Paystack, a leading Nigerian fintech payments company.', null::date, null, 'https://paystack.com/careers', 'https://ng.indeed.com/cmp/Paystack', 3, false, 'active', '{}'::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Paystack — Senior Backend Engineer (Abuja)',
       'Paystack',
       'job',
       'Nigeria (Abuja)',
       'Senior Backend Engineer role at Paystack, a leading Nigerian fintech payments company.',
       null::date,
       null,
       'https://paystack.com/careers',
       'https://ng.indeed.com/cmp/Paystack',
       3,
       false,
       'active',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Paystack — Senior Backend Engineer (Abuja)'
    and organization is not distinct from 'Paystack'
);

update opportunities set
    title = 'ActionAid International — Conflict Sensitivity Advisor (Nigeria)',
    organization = 'ActionAid International',
    category = 'job',
    geography = 'Nigeria',
    description = 'Conflict Sensitivity Advisor role with ActionAid International''s Nigeria programme.',
    deadline = date '2026-10-04',
    eligibility_notes = null,
    application_url = 'https://opportunitydesk.org/2026/10/01/30-hot-jobs-across-africa-currently-open-october-2-2026/',
    source_url = 'https://opportunitydesk.org/2026/10/01/30-hot-jobs-across-africa-currently-open-october-2-2026/',
    quality_rating = 1,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'ActionAid International — Conflict Sensitivity Advisor (Nigeria)'
  and organization is not distinct from 'ActionAid International'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('ActionAid International — Conflict Sensitivity Advisor (Nigeria)', 'ActionAid International', 'job', 'Nigeria', 'Conflict Sensitivity Advisor role with ActionAid International''s Nigeria programme.', date '2026-10-04', null, 'https://opportunitydesk.org/2026/10/01/30-hot-jobs-across-africa-currently-open-october-2-2026/', 'https://opportunitydesk.org/2026/10/01/30-hot-jobs-across-africa-currently-open-october-2-2026/', 1, false, 'active', array['NG']::text[], '{}'::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'ActionAid International — Conflict Sensitivity Advisor (Nigeria)',
       'ActionAid International',
       'job',
       'Nigeria',
       'Conflict Sensitivity Advisor role with ActionAid International''s Nigeria programme.',
       date '2026-10-04',
       null,
       'https://opportunitydesk.org/2026/10/01/30-hot-jobs-across-africa-currently-open-october-2-2026/',
       'https://opportunitydesk.org/2026/10/01/30-hot-jobs-across-africa-currently-open-october-2-2026/',
       1,
       false,
       'active',
       array['NG']::text[],
       '{}'::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'ActionAid International — Conflict Sensitivity Advisor (Nigeria)'
    and organization is not distinct from 'ActionAid International'
);
