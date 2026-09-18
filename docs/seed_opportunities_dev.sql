-- GENERATED from docs/OPZY_SOURCE_TRACKING.xlsx by backend/scripts/seed_opportunities.py.
-- Don't edit by hand: edit the sheet, then run `python -m scripts.seed_opportunities --sql`.
--
-- DEV/TEST DATA: includes fictional opportunities (see the sheet's Notes column).
-- Never run this against production.
--
-- Safe to re-run: rows already present (same title and organization) are skipped.

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Chevening Scholarship'
    and organization is not distinct from 'UK FCDO'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'World Bank Young Professionals Program (2027 cycle)'
    and organization is not distinct from 'World Bank Group'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'EBID Young Professional Programme'
    and organization is not distinct from 'ECOWAS Bank for Investment and Development'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Wetech x Nexascale AI Hackathon'
    and organization is not distinct from 'Wetech / Nexascale'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Junior Backend Engineer'
    and organization is not distinct from 'Kora Labs (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Graduate Data Analyst'
    and organization is not distinct from 'Sahel Insights (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Remote Customer Success Associate'
    and organization is not distinct from 'Brightline Africa (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Product Design Intern'
    and organization is not distinct from 'Tiwa Studio (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Software Engineering Internship (Summer 2027)'
    and organization is not distinct from 'Northstar Tech (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'expired'
where not exists (
  select 1 from opportunities
  where title = 'Agritech Research Internship'
    and organization is not distinct from 'Green Savanna Institute (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Future Leaders Undergraduate Scholarship'
    and organization is not distinct from 'Adeyemi Foundation (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Women in STEM Master''s Scholarship'
    and organization is not distinct from 'Aurora Education Trust (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Postgraduate Research Bursary'
    and organization is not distinct from 'Lakeside University Fund (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Civic Tech Fellowship'
    and organization is not distinct from 'OpenCity Collective (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'expired'
where not exists (
  select 1 from opportunities
  where title = 'Climate Innovators Fellowship'
    and organization is not distinct from 'Harmattan Fund (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Early-Stage Founder Grant'
    and organization is not distinct from 'Delta Ventures Foundation (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Creative Arts Micro-Grant'
    and organization is not distinct from 'Oriki Arts Council (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Health Innovation Research Grant'
    and organization is not distinct from 'Meridian Health Trust (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'FinTech Build Weekend'
    and organization is not distinct from 'Naija Devs Community (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'expired'
where not exists (
  select 1 from opportunities
  where title = 'Open Data Hack Abuja'
    and organization is not distinct from 'Civic Data Lab (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'Pan-African Pitch Competition'
    and organization is not distinct from 'Savanna Startup Network (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'active'
where not exists (
  select 1 from opportunities
  where title = 'National Essay Competition'
    and organization is not distinct from 'Unity Letters Society (fictional)'
);

insert into opportunities (title, organization, category, geography, description, deadline, eligibility_notes, application_url, source_url, quality_rating, verified, status)
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
       'removed'
where not exists (
  select 1 from opportunities
  where title = 'Campus Coding Challenge (withdrawn)'
    and organization is not distinct from 'ByteForge (fictional)'
);
