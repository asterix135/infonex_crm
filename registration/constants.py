"""Constants for use in other modules"""

PAYMENT_METHODS = (('V', 'Visa'),
                   ('M', 'MasterCard'),
                   ('A', 'AMEX'),
                   ('C', 'Cheque'),
                   ('W', 'Wire Transfer'),
                   ('N', 'Credit Note'),
                   ('O', 'Other method'))

REG_STATUS_OPTIONS = (('', '-----------'),
                      ('DU', 'Delegate Unpaid'),
                      ('DP', 'Delegate Paid'),
                      ('DF', 'Delegate Free'),
                      ('K', 'Speaker'),
                      ('SP', 'Sponsor Paid'),
                      ('SU', 'Sponsor Unpaid'),
                      ('SD', 'Sponsor Delegate'),
                      ('SE', 'Sponsor Exhibitor'),
                      ('G', 'Guest'),
                      ('DX', 'Delegate cancelled - paid'),
                      ('UX', 'Delegate cancelled - unpaid'),
                      ('SX', 'Sponsor cancelled'),
                      ('KX', 'Speaker cancelled'),
                      ('B', 'Substituted Out'))

CONTACT_OPTIONS = (('D', 'Attention: delegate'),
                   ('A', 'Attention: assistant'),
                   ('C', 'cc to Assistant'))

ADMIN_REPORTS = (('Delegate', 'Delegate List'),
                 ('NoName', 'No-Name Delegate List'),
                 ('Registration', 'Registration List'),
                 ('Phone', 'Phone/Email List'),
                 ('Onsite', 'Onsite Delegate List'),
                 ('Unpaid', 'Unpaid Delegate List'),
                 ('CE', 'CE Sign-in Sheet'),
                 ('Badges', 'Badges'),
                 ('Counts', 'Registration Counts'),
                 ('Speaker', 'Speaker List'),)

MASS_MAIL_CHOICES = (('venue', 'Venue Announcement'),
                     ('docs', 'Doc Download Instructions'),
                     ('thanks', 'Thank You For Attending'))

STATE_PROV_TUPLE =  (
    ('', 'Any'),
    ('AB', 'Alberta'), ('BC', 'British Columbia'), ('MB', 'Manitoba'),
    ('NB', 'New Brunswick'), ('NL', 'Newfoundland and Labrador'),
    ('NT', 'Northwest Territories'), ('NS', 'Nova Scotia'),
    ('NU', 'Nunavut'), ('ON', 'Ontario'),
    ('PEI', 'Prince Edward Island'), ('QC', 'Quebec'),
    ('SK', 'Saskatchewan'), ('YK', 'Yukon'),

    ('', '-----------'),

    ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'),
    ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'),
    ('CT', 'Connecticut'), ('DE', 'Delaware'),
    ('DC', 'District of Columbia'), ('FL', 'Florida'),
    ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
    ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
    ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'),
    ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'),
    ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
    ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'),
    ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'),
    ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
    ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'), ('SD', 'South Dakota'),
    ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
    ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'),
    ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')
)
