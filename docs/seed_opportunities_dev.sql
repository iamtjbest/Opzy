-- GENERATED from docs/OPZY_SOURCE_TRACKING.xlsx by backend/scripts/seed_opportunities.py.
-- Don't edit by hand: edit the sheet, then run `python -m scripts.seed_opportunities --sql`.
--
-- DEV/TEST DATA: includes fictional opportunities (see the sheet's Notes column).
-- Never run this against production.
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
    title = 'Junior Backend Engineer',
    organization = 'Kora Labs (fictional)',
    category = 'job',
    geography = 'Lagos',
    description = 'Build and maintain Python APIs for a payments product. Hybrid, three days a week in the Yaba office.',
    deadline = date '2026-10-15',
    eligibility_notes = '0–2 years experience; Python or Go; NYSC completed or exempted',
    application_url = 'https://example.com/kora-labs/backend',
    source_url = 'https://example.com/source/kora-labs',
    quality_rating = 4,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = array['graduate', 'postgraduate']::text[],
    fields_of_study = array['Computer Science', 'Computer Engineering', 'Software Engineering']::text[],
    skills = array['Python', 'Go', 'SQL']::text[],
    updated_at = now()
where title = 'Junior Backend Engineer'
  and organization is not distinct from 'Kora Labs (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Junior Backend Engineer', 'Kora Labs (fictional)', 'job', 'Lagos', 'Build and maintain Python APIs for a payments product. Hybrid, three days a week in the Yaba office.', date '2026-10-15', '0–2 years experience; Python or Go; NYSC completed or exempted', 'https://example.com/kora-labs/backend', 'https://example.com/source/kora-labs', 4, false, 'active', array['NG']::text[], array['graduate', 'postgraduate']::text[], array['Computer Science', 'Computer Engineering', 'Software Engineering']::text[], array['Python', 'Go', 'SQL']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Junior Backend Engineer',
       'Kora Labs (fictional)',
       'job',
       'Lagos',
       'Build and maintain Python APIs for a payments product. Hybrid, three days a week in the Yaba office.',
       date '2026-10-15',
       '0–2 years experience; Python or Go; NYSC completed or exempted',
       'https://example.com/kora-labs/backend',
       'https://example.com/source/kora-labs',
       4,
       false,
       'active',
       array['NG']::text[],
       array['graduate', 'postgraduate']::text[],
       array['Computer Science', 'Computer Engineering', 'Software Engineering']::text[],
       array['Python', 'Go', 'SQL']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Junior Backend Engineer'
    and organization is not distinct from 'Kora Labs (fictional)'
);

update opportunities set
    title = 'Graduate Data Analyst',
    organization = 'Sahel Insights (fictional)',
    category = 'job',
    geography = 'Abuja',
    description = 'Entry-level analyst role supporting public-sector research projects with SQL and dashboards.',
    deadline = date '2026-11-01',
    eligibility_notes = 'BSc in a quantitative field; SQL required; Excel/Power BI a plus',
    application_url = 'https://example.com/sahel-insights/analyst',
    source_url = 'https://example.com/source/sahel',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = array['graduate', 'postgraduate']::text[],
    fields_of_study = array['Mathematics', 'Statistics', 'Economics', 'Computer Science', 'Engineering', 'Physics']::text[],
    skills = array['SQL', 'Excel', 'Power BI']::text[],
    updated_at = now()
where title = 'Graduate Data Analyst'
  and organization is not distinct from 'Sahel Insights (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Graduate Data Analyst', 'Sahel Insights (fictional)', 'job', 'Abuja', 'Entry-level analyst role supporting public-sector research projects with SQL and dashboards.', date '2026-11-01', 'BSc in a quantitative field; SQL required; Excel/Power BI a plus', 'https://example.com/sahel-insights/analyst', 'https://example.com/source/sahel', 3, false, 'active', array['NG']::text[], array['graduate', 'postgraduate']::text[], array['Mathematics', 'Statistics', 'Economics', 'Computer Science', 'Engineering', 'Physics']::text[], array['SQL', 'Excel', 'Power BI']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Graduate Data Analyst',
       'Sahel Insights (fictional)',
       'job',
       'Abuja',
       'Entry-level analyst role supporting public-sector research projects with SQL and dashboards.',
       date '2026-11-01',
       'BSc in a quantitative field; SQL required; Excel/Power BI a plus',
       'https://example.com/sahel-insights/analyst',
       'https://example.com/source/sahel',
       3,
       false,
       'active',
       array['NG']::text[],
       array['graduate', 'postgraduate']::text[],
       array['Mathematics', 'Statistics', 'Economics', 'Computer Science', 'Engineering', 'Physics']::text[],
       array['SQL', 'Excel', 'Power BI']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Graduate Data Analyst'
    and organization is not distinct from 'Sahel Insights (fictional)'
);

update opportunities set
    title = 'Remote Customer Success Associate',
    organization = 'Brightline Africa (fictional)',
    category = 'job',
    geography = 'Remote (Nigeria)',
    description = 'Support SME customers across West Africa on a SaaS bookkeeping tool.',
    deadline = null::date,
    eligibility_notes = 'Strong written English; any degree; available 9am–5pm WAT',
    application_url = 'https://example.com/brightline/cs',
    source_url = 'https://example.com/source/brightline',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = array['graduate', 'postgraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = array['Customer Service', 'Writing', 'Communication']::text[],
    updated_at = now()
where title = 'Remote Customer Success Associate'
  and organization is not distinct from 'Brightline Africa (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Remote Customer Success Associate', 'Brightline Africa (fictional)', 'job', 'Remote (Nigeria)', 'Support SME customers across West Africa on a SaaS bookkeeping tool.', null::date, 'Strong written English; any degree; available 9am–5pm WAT', 'https://example.com/brightline/cs', 'https://example.com/source/brightline', 3, false, 'active', array['NG']::text[], array['graduate', 'postgraduate']::text[], '{}'::text[], array['Customer Service', 'Writing', 'Communication']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Remote Customer Success Associate',
       'Brightline Africa (fictional)',
       'job',
       'Remote (Nigeria)',
       'Support SME customers across West Africa on a SaaS bookkeeping tool.',
       null::date,
       'Strong written English; any degree; available 9am–5pm WAT',
       'https://example.com/brightline/cs',
       'https://example.com/source/brightline',
       3,
       false,
       'active',
       array['NG']::text[],
       array['graduate', 'postgraduate']::text[],
       '{}'::text[],
       array['Customer Service', 'Writing', 'Communication']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Remote Customer Success Associate'
    and organization is not distinct from 'Brightline Africa (fictional)'
);

update opportunities set
    title = 'Product Design Intern',
    organization = 'Tiwa Studio (fictional)',
    category = 'internship',
    geography = 'Lagos',
    description = 'Six-month paid internship on a fintech design team, working on mobile onboarding flows.',
    deadline = date '2026-10-10',
    eligibility_notes = 'Final-year students or recent graduates; portfolio required',
    application_url = 'https://example.com/tiwa/design-intern',
    source_url = 'https://example.com/source/tiwa',
    quality_rating = 4,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = array['undergraduate', 'graduate']::text[],
    fields_of_study = '{}'::text[],
    skills = array['Figma', 'UI Design', 'UX Research']::text[],
    updated_at = now()
where title = 'Product Design Intern'
  and organization is not distinct from 'Tiwa Studio (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Product Design Intern', 'Tiwa Studio (fictional)', 'internship', 'Lagos', 'Six-month paid internship on a fintech design team, working on mobile onboarding flows.', date '2026-10-10', 'Final-year students or recent graduates; portfolio required', 'https://example.com/tiwa/design-intern', 'https://example.com/source/tiwa', 4, false, 'active', '{}'::text[], array['undergraduate', 'graduate']::text[], '{}'::text[], array['Figma', 'UI Design', 'UX Research']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Product Design Intern',
       'Tiwa Studio (fictional)',
       'internship',
       'Lagos',
       'Six-month paid internship on a fintech design team, working on mobile onboarding flows.',
       date '2026-10-10',
       'Final-year students or recent graduates; portfolio required',
       'https://example.com/tiwa/design-intern',
       'https://example.com/source/tiwa',
       4,
       false,
       'active',
       '{}'::text[],
       array['undergraduate', 'graduate']::text[],
       '{}'::text[],
       array['Figma', 'UI Design', 'UX Research']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Product Design Intern'
    and organization is not distinct from 'Tiwa Studio (fictional)'
);

update opportunities set
    title = 'Software Engineering Internship (Summer 2027)',
    organization = 'Northstar Tech (fictional)',
    category = 'internship',
    geography = 'Global, open to Nigerians',
    description = '12-week remote internship pairing interns with senior engineers on production features.',
    deadline = date '2026-12-01',
    eligibility_notes = 'Currently enrolled in a CS or related degree; must graduate after June 2027',
    application_url = 'https://example.com/northstar/swe-intern',
    source_url = 'https://example.com/source/northstar',
    quality_rating = 5,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = array['undergraduate', 'postgraduate']::text[],
    fields_of_study = array['Computer Science', 'Computer Engineering', 'Software Engineering', 'Information Technology']::text[],
    skills = array['Python', 'Java', 'Data Structures']::text[],
    updated_at = now()
where title = 'Software Engineering Internship (Summer 2027)'
  and organization is not distinct from 'Northstar Tech (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Software Engineering Internship (Summer 2027)', 'Northstar Tech (fictional)', 'internship', 'Global, open to Nigerians', '12-week remote internship pairing interns with senior engineers on production features.', date '2026-12-01', 'Currently enrolled in a CS or related degree; must graduate after June 2027', 'https://example.com/northstar/swe-intern', 'https://example.com/source/northstar', 5, false, 'active', '{}'::text[], array['undergraduate', 'postgraduate']::text[], array['Computer Science', 'Computer Engineering', 'Software Engineering', 'Information Technology']::text[], array['Python', 'Java', 'Data Structures']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Software Engineering Internship (Summer 2027)',
       'Northstar Tech (fictional)',
       'internship',
       'Global, open to Nigerians',
       '12-week remote internship pairing interns with senior engineers on production features.',
       date '2026-12-01',
       'Currently enrolled in a CS or related degree; must graduate after June 2027',
       'https://example.com/northstar/swe-intern',
       'https://example.com/source/northstar',
       5,
       false,
       'active',
       '{}'::text[],
       array['undergraduate', 'postgraduate']::text[],
       array['Computer Science', 'Computer Engineering', 'Software Engineering', 'Information Technology']::text[],
       array['Python', 'Java', 'Data Structures']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Software Engineering Internship (Summer 2027)'
    and organization is not distinct from 'Northstar Tech (fictional)'
);

update opportunities set
    title = 'Agritech Research Internship',
    organization = 'Green Savanna Institute (fictional)',
    category = 'internship',
    geography = 'Ibadan',
    description = 'Three-month field and lab internship on crop yield data collection.',
    deadline = date '2026-09-01',
    eligibility_notes = 'Undergraduates in agriculture, biology, or statistics',
    application_url = 'https://example.com/green-savanna/intern',
    source_url = 'https://example.com/source/green-savanna',
    quality_rating = 3,
    verified = false,
    status = 'expired',
    eligible_countries = array['NG']::text[],
    education_levels = array['undergraduate']::text[],
    fields_of_study = array['Agriculture', 'Biology', 'Statistics']::text[],
    skills = array['Data Analysis']::text[],
    updated_at = now()
where title = 'Agritech Research Internship'
  and organization is not distinct from 'Green Savanna Institute (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Agritech Research Internship', 'Green Savanna Institute (fictional)', 'internship', 'Ibadan', 'Three-month field and lab internship on crop yield data collection.', date '2026-09-01', 'Undergraduates in agriculture, biology, or statistics', 'https://example.com/green-savanna/intern', 'https://example.com/source/green-savanna', 3, false, 'expired', array['NG']::text[], array['undergraduate']::text[], array['Agriculture', 'Biology', 'Statistics']::text[], array['Data Analysis']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Agritech Research Internship',
       'Green Savanna Institute (fictional)',
       'internship',
       'Ibadan',
       'Three-month field and lab internship on crop yield data collection.',
       date '2026-09-01',
       'Undergraduates in agriculture, biology, or statistics',
       'https://example.com/green-savanna/intern',
       'https://example.com/source/green-savanna',
       3,
       false,
       'expired',
       array['NG']::text[],
       array['undergraduate']::text[],
       array['Agriculture', 'Biology', 'Statistics']::text[],
       array['Data Analysis']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Agritech Research Internship'
    and organization is not distinct from 'Green Savanna Institute (fictional)'
);

update opportunities set
    title = 'Future Leaders Undergraduate Scholarship',
    organization = 'Adeyemi Foundation (fictional)',
    category = 'scholarship',
    geography = 'Nigeria',
    description = 'Full tuition plus a monthly stipend for undergraduates at Nigerian federal universities.',
    deadline = date '2026-11-20',
    eligibility_notes = 'Nigerian citizens; 200–300 level; minimum CGPA 3.5/5.0; family income below threshold',
    application_url = 'https://example.com/adeyemi/scholarship',
    source_url = 'https://example.com/source/adeyemi',
    quality_rating = 4,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = array['undergraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Future Leaders Undergraduate Scholarship'
  and organization is not distinct from 'Adeyemi Foundation (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Future Leaders Undergraduate Scholarship', 'Adeyemi Foundation (fictional)', 'scholarship', 'Nigeria', 'Full tuition plus a monthly stipend for undergraduates at Nigerian federal universities.', date '2026-11-20', 'Nigerian citizens; 200–300 level; minimum CGPA 3.5/5.0; family income below threshold', 'https://example.com/adeyemi/scholarship', 'https://example.com/source/adeyemi', 4, false, 'active', array['NG']::text[], array['undergraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Future Leaders Undergraduate Scholarship',
       'Adeyemi Foundation (fictional)',
       'scholarship',
       'Nigeria',
       'Full tuition plus a monthly stipend for undergraduates at Nigerian federal universities.',
       date '2026-11-20',
       'Nigerian citizens; 200–300 level; minimum CGPA 3.5/5.0; family income below threshold',
       'https://example.com/adeyemi/scholarship',
       'https://example.com/source/adeyemi',
       4,
       false,
       'active',
       array['NG']::text[],
       array['undergraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Future Leaders Undergraduate Scholarship'
    and organization is not distinct from 'Adeyemi Foundation (fictional)'
);

update opportunities set
    title = 'Women in STEM Master''s Scholarship',
    organization = 'Aurora Education Trust (fictional)',
    category = 'scholarship',
    geography = 'Nigeria (study abroad)',
    description = 'Funds a one-year STEM master''s degree at a partner university in Europe.',
    deadline = date '2027-01-15',
    eligibility_notes = 'Women; Nigerian nationals; first-class or 2:1 in a STEM field',
    application_url = 'https://example.com/aurora/stem',
    source_url = 'https://example.com/source/aurora',
    quality_rating = 5,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = array['graduate']::text[],
    fields_of_study = array['Science', 'Technology', 'Engineering', 'Mathematics', 'Computer Science', 'Physics', 'Chemistry', 'Biology']::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Women in STEM Master''s Scholarship'
  and organization is not distinct from 'Aurora Education Trust (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Women in STEM Master''s Scholarship', 'Aurora Education Trust (fictional)', 'scholarship', 'Nigeria (study abroad)', 'Funds a one-year STEM master''s degree at a partner university in Europe.', date '2027-01-15', 'Women; Nigerian nationals; first-class or 2:1 in a STEM field', 'https://example.com/aurora/stem', 'https://example.com/source/aurora', 5, false, 'active', array['NG']::text[], array['graduate']::text[], array['Science', 'Technology', 'Engineering', 'Mathematics', 'Computer Science', 'Physics', 'Chemistry', 'Biology']::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Women in STEM Master''s Scholarship',
       'Aurora Education Trust (fictional)',
       'scholarship',
       'Nigeria (study abroad)',
       'Funds a one-year STEM master''s degree at a partner university in Europe.',
       date '2027-01-15',
       'Women; Nigerian nationals; first-class or 2:1 in a STEM field',
       'https://example.com/aurora/stem',
       'https://example.com/source/aurora',
       5,
       false,
       'active',
       array['NG']::text[],
       array['graduate']::text[],
       array['Science', 'Technology', 'Engineering', 'Mathematics', 'Computer Science', 'Physics', 'Chemistry', 'Biology']::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Women in STEM Master''s Scholarship'
    and organization is not distinct from 'Aurora Education Trust (fictional)'
);

update opportunities set
    title = 'Postgraduate Research Bursary',
    organization = 'Lakeside University Fund (fictional)',
    category = 'scholarship',
    geography = 'ECOWAS region',
    description = 'Partial bursary for MSc and PhD candidates researching climate adaptation.',
    deadline = null::date,
    eligibility_notes = 'ECOWAS nationals; admitted to a postgraduate programme',
    application_url = 'https://example.com/lakeside/bursary',
    source_url = 'https://example.com/source/lakeside',
    quality_rating = 2,
    verified = false,
    status = 'active',
    eligible_countries = array['BJ', 'CI', 'CV', 'GH', 'GM', 'GN', 'GW', 'LR', 'NG', 'SL', 'SN', 'TG']::text[],
    education_levels = array['postgraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Postgraduate Research Bursary'
  and organization is not distinct from 'Lakeside University Fund (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Postgraduate Research Bursary', 'Lakeside University Fund (fictional)', 'scholarship', 'ECOWAS region', 'Partial bursary for MSc and PhD candidates researching climate adaptation.', null::date, 'ECOWAS nationals; admitted to a postgraduate programme', 'https://example.com/lakeside/bursary', 'https://example.com/source/lakeside', 2, false, 'active', array['BJ', 'CI', 'CV', 'GH', 'GM', 'GN', 'GW', 'LR', 'NG', 'SL', 'SN', 'TG']::text[], array['postgraduate']::text[], '{}'::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Postgraduate Research Bursary',
       'Lakeside University Fund (fictional)',
       'scholarship',
       'ECOWAS region',
       'Partial bursary for MSc and PhD candidates researching climate adaptation.',
       null::date,
       'ECOWAS nationals; admitted to a postgraduate programme',
       'https://example.com/lakeside/bursary',
       'https://example.com/source/lakeside',
       2,
       false,
       'active',
       array['BJ', 'CI', 'CV', 'GH', 'GM', 'GN', 'GW', 'LR', 'NG', 'SL', 'SN', 'TG']::text[],
       array['postgraduate']::text[],
       '{}'::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Postgraduate Research Bursary'
    and organization is not distinct from 'Lakeside University Fund (fictional)'
);

update opportunities set
    title = 'Civic Tech Fellowship',
    organization = 'OpenCity Collective (fictional)',
    category = 'fellowship',
    geography = 'Abuja',
    description = 'Nine-month paid fellowship building digital tools with state government agencies.',
    deadline = date '2026-10-25',
    eligibility_notes = 'Under 30; software, design, or policy background',
    application_url = 'https://example.com/opencity/fellowship',
    source_url = 'https://example.com/source/opencity',
    quality_rating = 4,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = '{}'::text[],
    fields_of_study = array['Computer Science', 'Software Engineering', 'Design', 'Public Policy', 'Political Science']::text[],
    skills = array['Python', 'JavaScript', 'Figma', 'Policy Analysis']::text[],
    updated_at = now()
where title = 'Civic Tech Fellowship'
  and organization is not distinct from 'OpenCity Collective (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Civic Tech Fellowship', 'OpenCity Collective (fictional)', 'fellowship', 'Abuja', 'Nine-month paid fellowship building digital tools with state government agencies.', date '2026-10-25', 'Under 30; software, design, or policy background', 'https://example.com/opencity/fellowship', 'https://example.com/source/opencity', 4, false, 'active', array['NG']::text[], '{}'::text[], array['Computer Science', 'Software Engineering', 'Design', 'Public Policy', 'Political Science']::text[], array['Python', 'JavaScript', 'Figma', 'Policy Analysis']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Civic Tech Fellowship',
       'OpenCity Collective (fictional)',
       'fellowship',
       'Abuja',
       'Nine-month paid fellowship building digital tools with state government agencies.',
       date '2026-10-25',
       'Under 30; software, design, or policy background',
       'https://example.com/opencity/fellowship',
       'https://example.com/source/opencity',
       4,
       false,
       'active',
       array['NG']::text[],
       '{}'::text[],
       array['Computer Science', 'Software Engineering', 'Design', 'Public Policy', 'Political Science']::text[],
       array['Python', 'JavaScript', 'Figma', 'Policy Analysis']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Civic Tech Fellowship'
    and organization is not distinct from 'OpenCity Collective (fictional)'
);

update opportunities set
    title = 'Climate Innovators Fellowship',
    organization = 'Harmattan Fund (fictional)',
    category = 'fellowship',
    geography = 'Global, open to Nigerians',
    description = 'Six-month virtual fellowship with mentorship and seed funding for climate projects.',
    deadline = date '2026-08-15',
    eligibility_notes = 'Aged 18–35; working on an early-stage climate project',
    application_url = 'https://example.com/harmattan/fellowship',
    source_url = 'https://example.com/source/harmattan',
    quality_rating = 4,
    verified = false,
    status = 'expired',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = array['Environmental Science']::text[],
    skills = '{}'::text[],
    updated_at = now()
where title = 'Climate Innovators Fellowship'
  and organization is not distinct from 'Harmattan Fund (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Climate Innovators Fellowship', 'Harmattan Fund (fictional)', 'fellowship', 'Global, open to Nigerians', 'Six-month virtual fellowship with mentorship and seed funding for climate projects.', date '2026-08-15', 'Aged 18–35; working on an early-stage climate project', 'https://example.com/harmattan/fellowship', 'https://example.com/source/harmattan', 4, false, 'expired', '{}'::text[], '{}'::text[], array['Environmental Science']::text[], '{}'::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Climate Innovators Fellowship',
       'Harmattan Fund (fictional)',
       'fellowship',
       'Global, open to Nigerians',
       'Six-month virtual fellowship with mentorship and seed funding for climate projects.',
       date '2026-08-15',
       'Aged 18–35; working on an early-stage climate project',
       'https://example.com/harmattan/fellowship',
       'https://example.com/source/harmattan',
       4,
       false,
       'expired',
       '{}'::text[],
       '{}'::text[],
       array['Environmental Science']::text[],
       '{}'::text[]
where not exists (
  select 1 from opportunities
  where title = 'Climate Innovators Fellowship'
    and organization is not distinct from 'Harmattan Fund (fictional)'
);

update opportunities set
    title = 'Early-Stage Founder Grant',
    organization = 'Delta Ventures Foundation (fictional)',
    category = 'grant',
    geography = 'Nigeria',
    description = 'Non-equity grant of up to ₦5,000,000 for pre-seed startups.',
    deadline = date '2026-11-30',
    eligibility_notes = 'Registered Nigerian business under 2 years old; at least one full-time founder',
    application_url = 'https://example.com/delta/grant',
    source_url = 'https://example.com/source/delta',
    quality_rating = 4,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = array['Entrepreneurship']::text[],
    updated_at = now()
where title = 'Early-Stage Founder Grant'
  and organization is not distinct from 'Delta Ventures Foundation (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Early-Stage Founder Grant', 'Delta Ventures Foundation (fictional)', 'grant', 'Nigeria', 'Non-equity grant of up to ₦5,000,000 for pre-seed startups.', date '2026-11-30', 'Registered Nigerian business under 2 years old; at least one full-time founder', 'https://example.com/delta/grant', 'https://example.com/source/delta', 4, false, 'active', array['NG']::text[], '{}'::text[], '{}'::text[], array['Entrepreneurship']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Early-Stage Founder Grant',
       'Delta Ventures Foundation (fictional)',
       'grant',
       'Nigeria',
       'Non-equity grant of up to ₦5,000,000 for pre-seed startups.',
       date '2026-11-30',
       'Registered Nigerian business under 2 years old; at least one full-time founder',
       'https://example.com/delta/grant',
       'https://example.com/source/delta',
       4,
       false,
       'active',
       array['NG']::text[],
       '{}'::text[],
       '{}'::text[],
       array['Entrepreneurship']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Early-Stage Founder Grant'
    and organization is not distinct from 'Delta Ventures Foundation (fictional)'
);

update opportunities set
    title = 'Creative Arts Micro-Grant',
    organization = 'Oriki Arts Council (fictional)',
    category = 'grant',
    geography = 'Lagos',
    description = 'Small grants for visual artists, writers, and filmmakers producing new work.',
    deadline = null::date,
    eligibility_notes = 'Lagos residents; aged 18+; portfolio or writing sample required',
    application_url = 'https://example.com/oriki/grant',
    source_url = 'https://example.com/source/oriki',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = '{}'::text[],
    fields_of_study = array['Fine Arts', 'Creative Writing', 'Music', 'Film']::text[],
    skills = array['Writing', 'Illustration', 'Photography']::text[],
    updated_at = now()
where title = 'Creative Arts Micro-Grant'
  and organization is not distinct from 'Oriki Arts Council (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Creative Arts Micro-Grant', 'Oriki Arts Council (fictional)', 'grant', 'Lagos', 'Small grants for visual artists, writers, and filmmakers producing new work.', null::date, 'Lagos residents; aged 18+; portfolio or writing sample required', 'https://example.com/oriki/grant', 'https://example.com/source/oriki', 3, false, 'active', array['NG']::text[], '{}'::text[], array['Fine Arts', 'Creative Writing', 'Music', 'Film']::text[], array['Writing', 'Illustration', 'Photography']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Creative Arts Micro-Grant',
       'Oriki Arts Council (fictional)',
       'grant',
       'Lagos',
       'Small grants for visual artists, writers, and filmmakers producing new work.',
       null::date,
       'Lagos residents; aged 18+; portfolio or writing sample required',
       'https://example.com/oriki/grant',
       'https://example.com/source/oriki',
       3,
       false,
       'active',
       array['NG']::text[],
       '{}'::text[],
       array['Fine Arts', 'Creative Writing', 'Music', 'Film']::text[],
       array['Writing', 'Illustration', 'Photography']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Creative Arts Micro-Grant'
    and organization is not distinct from 'Oriki Arts Council (fictional)'
);

update opportunities set
    title = 'Health Innovation Research Grant',
    organization = 'Meridian Health Trust (fictional)',
    category = 'grant',
    geography = 'ECOWAS region',
    description = 'Funding for applied research on primary healthcare delivery.',
    deadline = date '2027-02-28',
    eligibility_notes = 'Affiliated with a university or research institute in an ECOWAS country',
    application_url = 'https://example.com/meridian/grant',
    source_url = 'https://example.com/source/meridian',
    quality_rating = 3,
    verified = false,
    status = 'active',
    eligible_countries = array['BJ', 'CI', 'CV', 'GH', 'GM', 'GN', 'GW', 'LR', 'NG', 'SL', 'SN', 'TG']::text[],
    education_levels = array['postgraduate']::text[],
    fields_of_study = array['Medicine', 'Public Health', 'Pharmacy', 'Nursing', 'Biomedical Engineering']::text[],
    skills = array['Research']::text[],
    updated_at = now()
where title = 'Health Innovation Research Grant'
  and organization is not distinct from 'Meridian Health Trust (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Health Innovation Research Grant', 'Meridian Health Trust (fictional)', 'grant', 'ECOWAS region', 'Funding for applied research on primary healthcare delivery.', date '2027-02-28', 'Affiliated with a university or research institute in an ECOWAS country', 'https://example.com/meridian/grant', 'https://example.com/source/meridian', 3, false, 'active', array['BJ', 'CI', 'CV', 'GH', 'GM', 'GN', 'GW', 'LR', 'NG', 'SL', 'SN', 'TG']::text[], array['postgraduate']::text[], array['Medicine', 'Public Health', 'Pharmacy', 'Nursing', 'Biomedical Engineering']::text[], array['Research']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Health Innovation Research Grant',
       'Meridian Health Trust (fictional)',
       'grant',
       'ECOWAS region',
       'Funding for applied research on primary healthcare delivery.',
       date '2027-02-28',
       'Affiliated with a university or research institute in an ECOWAS country',
       'https://example.com/meridian/grant',
       'https://example.com/source/meridian',
       3,
       false,
       'active',
       array['BJ', 'CI', 'CV', 'GH', 'GM', 'GN', 'GW', 'LR', 'NG', 'SL', 'SN', 'TG']::text[],
       array['postgraduate']::text[],
       array['Medicine', 'Public Health', 'Pharmacy', 'Nursing', 'Biomedical Engineering']::text[],
       array['Research']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Health Innovation Research Grant'
    and organization is not distinct from 'Meridian Health Trust (fictional)'
);

update opportunities set
    title = 'FinTech Build Weekend',
    organization = 'Naija Devs Community (fictional)',
    category = 'hackathon',
    geography = 'Lagos',
    description = '48-hour in-person hackathon on financial inclusion, with ₦2,000,000 in prizes.',
    deadline = date '2026-10-03',
    eligibility_notes = 'Teams of 2–5; open to students and professionals',
    application_url = 'https://example.com/naijadevs/hackathon',
    source_url = 'https://example.com/source/naijadevs',
    quality_rating = 4,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = array['Python', 'JavaScript', 'Figma', 'Product Management']::text[],
    updated_at = now()
where title = 'FinTech Build Weekend'
  and organization is not distinct from 'Naija Devs Community (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('FinTech Build Weekend', 'Naija Devs Community (fictional)', 'hackathon', 'Lagos', '48-hour in-person hackathon on financial inclusion, with ₦2,000,000 in prizes.', date '2026-10-03', 'Teams of 2–5; open to students and professionals', 'https://example.com/naijadevs/hackathon', 'https://example.com/source/naijadevs', 4, false, 'active', '{}'::text[], '{}'::text[], '{}'::text[], array['Python', 'JavaScript', 'Figma', 'Product Management']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'FinTech Build Weekend',
       'Naija Devs Community (fictional)',
       'hackathon',
       'Lagos',
       '48-hour in-person hackathon on financial inclusion, with ₦2,000,000 in prizes.',
       date '2026-10-03',
       'Teams of 2–5; open to students and professionals',
       'https://example.com/naijadevs/hackathon',
       'https://example.com/source/naijadevs',
       4,
       false,
       'active',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       array['Python', 'JavaScript', 'Figma', 'Product Management']::text[]
where not exists (
  select 1 from opportunities
  where title = 'FinTech Build Weekend'
    and organization is not distinct from 'Naija Devs Community (fictional)'
);

update opportunities set
    title = 'Open Data Hack Abuja',
    organization = 'Civic Data Lab (fictional)',
    category = 'hackathon',
    geography = 'Abuja',
    description = 'Build tools on top of public government datasets.',
    deadline = date '2026-09-05',
    eligibility_notes = 'Open to all; beginners welcome',
    application_url = 'https://example.com/civicdata/hack',
    source_url = 'https://example.com/source/civicdata',
    quality_rating = 2,
    verified = false,
    status = 'expired',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = array['Data Analysis', 'Python']::text[],
    updated_at = now()
where title = 'Open Data Hack Abuja'
  and organization is not distinct from 'Civic Data Lab (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Open Data Hack Abuja', 'Civic Data Lab (fictional)', 'hackathon', 'Abuja', 'Build tools on top of public government datasets.', date '2026-09-05', 'Open to all; beginners welcome', 'https://example.com/civicdata/hack', 'https://example.com/source/civicdata', 2, false, 'expired', '{}'::text[], '{}'::text[], '{}'::text[], array['Data Analysis', 'Python']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Open Data Hack Abuja',
       'Civic Data Lab (fictional)',
       'hackathon',
       'Abuja',
       'Build tools on top of public government datasets.',
       date '2026-09-05',
       'Open to all; beginners welcome',
       'https://example.com/civicdata/hack',
       'https://example.com/source/civicdata',
       2,
       false,
       'expired',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       array['Data Analysis', 'Python']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Open Data Hack Abuja'
    and organization is not distinct from 'Civic Data Lab (fictional)'
);

update opportunities set
    title = 'Pan-African Pitch Competition',
    organization = 'Savanna Startup Network (fictional)',
    category = 'competition',
    geography = 'Global, open to Nigerians',
    description = 'Startup pitch competition with a $25,000 top prize and investor introductions.',
    deadline = date '2026-10-31',
    eligibility_notes = 'Africa-focused startups with a working product',
    application_url = 'https://example.com/savanna/pitch',
    source_url = 'https://example.com/source/savanna',
    quality_rating = 5,
    verified = false,
    status = 'active',
    eligible_countries = '{}'::text[],
    education_levels = '{}'::text[],
    fields_of_study = '{}'::text[],
    skills = array['Entrepreneurship', 'Public Speaking']::text[],
    updated_at = now()
where title = 'Pan-African Pitch Competition'
  and organization is not distinct from 'Savanna Startup Network (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Pan-African Pitch Competition', 'Savanna Startup Network (fictional)', 'competition', 'Global, open to Nigerians', 'Startup pitch competition with a $25,000 top prize and investor introductions.', date '2026-10-31', 'Africa-focused startups with a working product', 'https://example.com/savanna/pitch', 'https://example.com/source/savanna', 5, false, 'active', '{}'::text[], '{}'::text[], '{}'::text[], array['Entrepreneurship', 'Public Speaking']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Pan-African Pitch Competition',
       'Savanna Startup Network (fictional)',
       'competition',
       'Global, open to Nigerians',
       'Startup pitch competition with a $25,000 top prize and investor introductions.',
       date '2026-10-31',
       'Africa-focused startups with a working product',
       'https://example.com/savanna/pitch',
       'https://example.com/source/savanna',
       5,
       false,
       'active',
       '{}'::text[],
       '{}'::text[],
       '{}'::text[],
       array['Entrepreneurship', 'Public Speaking']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Pan-African Pitch Competition'
    and organization is not distinct from 'Savanna Startup Network (fictional)'
);

update opportunities set
    title = 'National Essay Competition',
    organization = 'Unity Letters Society (fictional)',
    category = 'competition',
    geography = 'Nigeria',
    description = 'Essay competition on youth and nation-building for secondary and tertiary students.',
    deadline = null::date,
    eligibility_notes = 'Nigerian students aged 16–25',
    application_url = 'https://example.com/unity/essay',
    source_url = 'https://example.com/source/unity',
    quality_rating = 2,
    verified = false,
    status = 'active',
    eligible_countries = array['NG']::text[],
    education_levels = array['secondary', 'undergraduate']::text[],
    fields_of_study = '{}'::text[],
    skills = array['Writing']::text[],
    updated_at = now()
where title = 'National Essay Competition'
  and organization is not distinct from 'Unity Letters Society (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('National Essay Competition', 'Unity Letters Society (fictional)', 'competition', 'Nigeria', 'Essay competition on youth and nation-building for secondary and tertiary students.', null::date, 'Nigerian students aged 16–25', 'https://example.com/unity/essay', 'https://example.com/source/unity', 2, false, 'active', array['NG']::text[], array['secondary', 'undergraduate']::text[], '{}'::text[], array['Writing']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'National Essay Competition',
       'Unity Letters Society (fictional)',
       'competition',
       'Nigeria',
       'Essay competition on youth and nation-building for secondary and tertiary students.',
       null::date,
       'Nigerian students aged 16–25',
       'https://example.com/unity/essay',
       'https://example.com/source/unity',
       2,
       false,
       'active',
       array['NG']::text[],
       array['secondary', 'undergraduate']::text[],
       '{}'::text[],
       array['Writing']::text[]
where not exists (
  select 1 from opportunities
  where title = 'National Essay Competition'
    and organization is not distinct from 'Unity Letters Society (fictional)'
);

update opportunities set
    title = 'Campus Coding Challenge (withdrawn)',
    organization = 'ByteForge (fictional)',
    category = 'competition',
    geography = 'Port Harcourt',
    description = 'Inter-university coding challenge. Withdrawn by the organiser; kept to exercise the ''removed'' status.',
    deadline = date '2026-10-20',
    eligibility_notes = 'University students in Rivers State',
    application_url = 'https://example.com/byteforge/challenge',
    source_url = 'https://example.com/source/byteforge',
    quality_rating = 1,
    verified = false,
    status = 'removed',
    eligible_countries = array['NG']::text[],
    education_levels = array['undergraduate']::text[],
    fields_of_study = array['Computer Science']::text[],
    skills = array['Python', 'Java']::text[],
    updated_at = now()
where title = 'Campus Coding Challenge (withdrawn)'
  and organization is not distinct from 'ByteForge (fictional)'
  and (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills) is distinct from ('Campus Coding Challenge (withdrawn)', 'ByteForge (fictional)', 'competition', 'Port Harcourt', 'Inter-university coding challenge. Withdrawn by the organiser; kept to exercise the ''removed'' status.', date '2026-10-20', 'University students in Rivers State', 'https://example.com/byteforge/challenge', 'https://example.com/source/byteforge', 1, false, 'removed', array['NG']::text[], array['undergraduate']::text[], array['Computer Science']::text[], array['Python', 'Java']::text[]);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status, eligible_countries, education_levels, fields_of_study, skills)
select 'Campus Coding Challenge (withdrawn)',
       'ByteForge (fictional)',
       'competition',
       'Port Harcourt',
       'Inter-university coding challenge. Withdrawn by the organiser; kept to exercise the ''removed'' status.',
       date '2026-10-20',
       'University students in Rivers State',
       'https://example.com/byteforge/challenge',
       'https://example.com/source/byteforge',
       1,
       false,
       'removed',
       array['NG']::text[],
       array['undergraduate']::text[],
       array['Computer Science']::text[],
       array['Python', 'Java']::text[]
where not exists (
  select 1 from opportunities
  where title = 'Campus Coding Challenge (withdrawn)'
    and organization is not distinct from 'ByteForge (fictional)'
);
