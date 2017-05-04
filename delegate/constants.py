PAID_STATUS_VALUES = ['DP', 'SP', 'DX', 'SX',]
UNPAID_STATUS_VALUES = ['DU', 'SU']
CXL_VALUES = ['DX', 'SX', 'KX']
NON_INVOICE_VALUES = ['K', 'KX', 'SD', 'SE', 'G', '']
NO_CONFIRMATION_VALUES = ['K', 'KX']
GUEST_CONFIRMATION = ['G', 'SD', 'SE']
SPONSOR_CONFIRMATION = ['SP', 'SU']

TRAINING_CO_WEBSITE = 'www.inx-training.com'
CANADA_WEBSITE = 'www.infonex.com'
US_WEBSITE = 'www.infonex.com'

CANADA_CXL_POLICY = 'Substitutions are welcome at any time.  If you have to ' \
    'cancel more than 14 days prior to the first day of the event, you will ' \
    'receive a credit voucher for the full amount, redeemable against any '\
    'other Infonex course.  If you cancel less than 14 days prior to the ' \
    'first day of the event, you will not be eligible to receive any credits ' \
    'and are liable for the entire registration fees.  All cancellations ' \
    'must be made in writing.'
USA_CXL_POLICY = CANADA_CXL_POLICY
TRAINING_CXL_POLICY = 'Due to demand and limited enrollment, there are no ' \
    'refunds or credit notes available for master class or seminar ' \
    'registrations. Substitutions may be made at any time. If you are unable ' \
    'to attend, a colleague may take your place at the event. Simply contact ' \
    'our registration department so we can transfer your registration and be ' \
    'sure your colleague receives full access to the event materials, a name ' \
    'badge, and a seat reserved at the master class or training seminar.'

STOPWORDS = ['&',
             '-',
             'a',
             'affairs',
             'agency',
             'alberta',
             'an',
             'and',
             'association',
             'bank',
             'bc',
             'board',
             'brunswick',
             'by',
             'canada',
             'canadian',
             'centre',
             'city',
             'college',
             'commission',
             'consulting',
             'company',
             'corp',
             'corp.',
             'corporation',
             'council',
             'department',
             'dept',
             'dept.',
             'development',
             'energy',
             'financial',
             'first',
             'for',
             'from',
             'gold',
             'group',
             'government',
             'health',
             'in',
             'inc',
             'inc.',
             'international',
             'llp',
             'llp.',
             'ltd',
             'ltd.',
             'management',
             'manitoba',
             'ministry',
             'nation',
             'national',
             'newfoundland',
             'of',
             'office',
             'on',
             'ontario',
             'or',
             'public',
             'quebec',
             'resources',
             'service',
             'services',
             'scotia',
             'the',
             'university',
            ]

SEARCH_SUBSTITUTIONS = (
    ('&', 'and'),
    ('AANDC', 'Indigenous and Norther Affairs'),
    ('ACOA', 'Atlantic Canada Opportunities Agency'),
    ('AESO', 'Alberta Electrical System Operator'),
    ('AMF', 'Autorité des marchés financiers'),
    ('BLG', 'Borden Ladner Gervais'),
    ('BMO', 'Bank of Montreal'),
    ('CAPE', 'Canadian Association of Professional Employees'),
    ('CATSA', 'Canadian Air Transport Security Authority'),
    ('CBC', 'Canadian Broadcasting Corporation'),
    ('CBSA', 'Canada Border Services Agency'),
    ('centre', 'center'),
    ('CFIA', 'Canadian Food Inpsection Agency'),
    ('CDIC', 'Canada Deposit Insurance Corporation'),
    ('CIHR', 'Canadian Institutes of Health Research'),
    ('CMHC', 'Canada Mortgage and Housing Corporation'),
    ('CN', 'Canadian National'),
    ('CP', 'Canadian Pacific'),
    ('CPA', 'Chartered Professional Accountants'),
    ('CRA', 'Canada Revenue Agency'),
    ('CSE', 'Communications Security Establishment'),
    ('CSIS', 'Canadian Security Intelligence Service'),
    ('Defense', 'Defense'),
    ('DND', 'Department of National Defence'),
    ('Environment Canada', 'Environment and Climate Change Canada'),
    ('ESDC', 'Employment and Social Development Canada'),
    ('EY', 'Ernst & Young'),
    ('IESO', 'Independent Electricity System Opreator'),
    ('IRB', 'Immigration and Refugee Board'),
    ('INAC', 'Indigenous and Northern Affairs Canada'),
    ('LCBO', 'Liquor Control Board of Ontario'),
    ('MCSS', 'Ministry of Community and Social Services'),
    ('MCYS', 'Ministry of Children and Youth Services'),
    ('MNP', 'Meyers Norris Penny'),
    ('MOT', 'Ministry of Transportation'),
    ('nation', 'nations'),
    ('NEB', 'National Energy Board'),
    ('NRC', 'National Research Council'),
    ('OEB', 'Ontario Energy Board'),
    ('OMAFRA', 'Ministry of Agriculture Food and Rural Affairs'),
    ('OPP', 'Ontario Provincial Police'),
    ('OSC', 'Ontario Securities Commission'),
    ('OSFI', 'Office of the Superintendent of Financial Institutions'),
    ('PSPC', 'Public Service and Procurement Canada'),
    ('PwC', 'PricewaterhouseCoopers'),
    ('PwC', 'Pricewaterhouse Coopers'),
    ('RBC', 'Royal Bank'),
    ('RCMP', 'Royal Canadian Mounted Police'),
    ('ServiceOntario', 'Service Ontario'),
    ('Sunlife', 'Sun Life'),
    ('TBS', 'Treasury Board Secretariat'),
    ('TD', 'Toronto Dominion'),
)
