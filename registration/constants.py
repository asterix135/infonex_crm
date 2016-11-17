"""Constants for use in other modules"""

PAYMENT_METHODS = (('V', 'Visa'),
                   ('M', 'MasterCard'),
                   ('A', 'AMEX'),
                   ('C', 'Cheque'),
                   ('W', 'Wire Transfer'),
                   ('N', 'Credit Note'),
                   ('O', 'Other method'))

REG_STATUS_OPTIONS = (('DP', 'Delegate Paid'),
                      ('DU', 'Delegate Unpaid'),
                      ('DF', 'Delegate Free'),
                      ('K', 'Speaker'),
                      ('SP', 'Sponsor Paid'),
                      ('SU', 'Sponsor Unpaid'),
                      ('SD', 'Sponsor Deposit Paid'),
                      ('G', 'Guest'),
                      ('DX', 'Delegate cancelled'),
                      ('SX', 'Sponsor cancelled'),
                      ('KX', 'Speaker cancelled'))

CONTACT_OPTIONS = (('D', 'Attention: delegate'),
                   ('A', 'Attention: assistant'),
                   ('C', 'cc to Assistant'))

COMPANY_OPTIONS = (('IC', 'Infonex Inc'),
                   ('IT', 'INX-Training'),
                   ('IU', 'Infonex (USA) Inc.'))

BILLING_CURRENCY = (('CAD', 'CAD'),
                    ('USD', 'USD'))
