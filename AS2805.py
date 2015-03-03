__author__ = 'arthurvandermerwe'

import struct

from Host_Node.AS2805Errors import *
import binascii
import string
from Shared.ByteUtils import HexToByte, ByteToHex


class AS2805:
    #Attributes
    # Bits to be set 00000000 -> _BIT_POSITION_1 ... _BIT_POSITION_8
    _BIT_POSITION_1 = 128 # 10 00 00 00
    _BIT_POSITION_2 = 64 # 01 00 00 00
    _BIT_POSITION_3 = 32 # 00 10 00 00
    _BIT_POSITION_4 = 16 # 00 01 00 00
    _BIT_POSITION_5 = 8 # 00 00 10 00
    _BIT_POSITION_6 = 4 # 00 00 01 00
    _BIT_POSITION_7 = 2 # 00 00 00 10
    _BIT_POSITION_8 = 1 # 00 00 00 01

    #Array to translate bit to position
    _TMP = [0, _BIT_POSITION_8, _BIT_POSITION_1, _BIT_POSITION_2, _BIT_POSITION_3, _BIT_POSITION_4, _BIT_POSITION_5,
            _BIT_POSITION_6, _BIT_POSITION_7]
    _EMPTY_VALUE = 0


    #2805 contants
    _DEF = {}
    # Every _DEF has:
    # _DEF[N] = [X, Y, Z, W, K, P, Q, W]
    # N = bitnumber
    # X = smallStr representation of the bit meanning
    # Y = large str representation
    # Z = length indicator of the bit (F, LL, LLL, LLLL, LLLLL, LLLLLL)
    # W = size of the information
    # K = type of values a, an, ans, as, b, ns, s, x, z, this is also the type of the length indicator
    # P = format of the message
    """
    Type	Meaning
    'b'	Binary format. Outputs the number in base 2.
    'c'	Character. Converts the integer to the corresponding unicode character before printing.
    'd'	Decimal Integer. Outputs the number in base 10.
    'o'	Octal format. Outputs the number in base 8.
    'x'	Hex format. Outputs the number in base 16, using lower- case letters for the digits above 9.
    'X'	Hex format. Outputs the number in base 16, using upper- case letters for the digits above 9.
    'n'	Number. This is the same as 'd', except that it uses the current locale setting to insert the appropriate number separator characters.
     None	The same as 'd'.
    """
    # Q = padding of the message - 0 / F or none
    # W = justification, left / right or none
    _DEF[1] = ['BM', 'Bit Map Extended',                        'F',    8,  'b',    'X',    'none',  'none']
    _DEF[2] = ['2', 'Primary Account Number (PAN)',             'LL',   19, 'n',    'c',    'F', 'left']
    _DEF[3] = ['3', 'Processing Code',                          'F',    6,  'n',    'n',    '0',  'right']
    _DEF[4] = ['4', 'Amount Transaction',                       'F',    12, 'n',    'c',    '0',  'right']
    _DEF[5] = ['5', 'Amount Settlement',                        'F',    12, 'n',    'c',    '0',  'right']
    _DEF[7] = ['7', 'Transmission Date and Time',               'F',    10, 'n',    'n',    '0',  'right']
    _DEF[9] = ['9', 'Conversion Rate, Settlement',              'F',    8,  'n',    'n',    '0',  'right']
    _DEF[10] = ['10', 'Conversion Rate, Cardholder Billing',    'F',    8,  'n',    'n',    '0',  'right']
    _DEF[11] = ['11', 'Systems Trace Audit Number',             'F',    6,  'n',    'n',    '0',  'right']
    _DEF[12] = ['12', 'Time, Local Transaction',                'F',    6,  'n',    'n',    '0',  'right']
    _DEF[13] = ['13', 'Date, Local Transaction',                'F',    4,  'n',    'n',    '0',  'right']
    _DEF[14] = ['14', 'Date, Expiration',                       'F',    4,  'n',    'n',    '0',  'right']
    _DEF[15] = ['15', 'Date, Settlement',                       'F',    4,  'n',    'n',    '0',  'right']
    _DEF[16] = ['16', 'Date, Conversion',                       'F',    4,  'n',    'n',    '0',  'right']
    _DEF[18] = ['18', 'Merchant Type',                          'F',    4,  'n',    'n',    '0',  'right']
    _DEF[19] = ['19', 'Acquiring Institution Country Code',     'F',    3,  'n',    'n',    '0',  'right']
    _DEF[20] = ['20', 'PAN Extended Country Code',              'F',    3,  'n',    'n',    '0',  'right']
    _DEF[21] = ['21', 'Forwarding Institution Country Code',    'F',    3,  'n',    'n',    '0',  'right']
    _DEF[22] = ['22', 'POS Entry Mode',                         'F',    3,  'n',    'n',    '0',  'right']
    _DEF[23] = ['23', 'Card Sequence Number',                   'F',    3,  'n',    'n',    '0',  'right']
    _DEF[25] = ['25', 'POS Condition Code',                     'F',    2,  'n',    'n',    '0',  'right']
    _DEF[28] = ['28', 'Amount, Transaction Fee',                'F',    9, 'xn',    'c',    '0',  'right']
    _DEF[29] = ['29', 'Amount, Settlement Fee',                 'F',    8, 'xn',    'c',    '0',  'right']
    _DEF[30] = ['30', 'Amount, Processing Fee',                 'F',    8, 'xn',    'c',    '0',  'right']
    _DEF[31] = ['31', 'Amount, Settlement Processing Fee',      'F',    8, 'xn',    'c',    '0',  'right']
    _DEF[32] = ['32', 'Acquiring Institution ID Code',         'LL',    11, 'n',    'c',    'F',   'left']
    _DEF[33] = ['33', 'Forwarding Institution ID Code',        'LL',    11, 'n',    'c',    'F',   'left']
    _DEF[34] = ['34', 'PAN Extended'                           'LL',    28,'ns',    'c',    'F',   'left']
    _DEF[35] = ['35', 'Track 2 Data',                          'LL',    37, 'z',    'c',    'F',   'left']
    _DEF[36] = ['36', 'Track 3 Data',                         '0LLL',   104, 'z',   'c',    'F',   'left']
    _DEF[37] = ['37', 'Retrieval Reference Number',             'F',   12, 'an',    'x',    '0',  'right']
    _DEF[38] = ['38', 'Authorization ID Response',              'F',    6, 'an',    'x',    '0',  'right']
    _DEF[39] = ['39', 'Response Code',                          'F',    2, 'an',    'x',    '0',  'right']
    _DEF[40] = ['40', 'Service Restriction Code',               'F',    3, 'an',    'x',    '0',  'right']
    _DEF[41] = ['41', 'Card Acceptor Terminal ID',              'F',    8, 'an',    'x',    '0',  'right']
    _DEF[42] = ['42', 'Card Acceptor ID Code',                  'F',   15, 'ans',    'x',    '0',  'right']
    _DEF[43] = ['43', 'Card Acceptor Name Location',            'F',   40, 'an',    'x',    '0',  'right']
    _DEF[44] = ['44', 'Additional Response Data',              'LL',  15, 'ans',    'x',    'F',   'left']
    _DEF[47] = ['47', 'Additional Data ISO',                  'LLL', 999, 'ans',    'x',    'F',   'left']
    _DEF[48] = ['48', 'Additional Data Private',              'LLL', 999, 'b',    'x',    'F',   'left']
    _DEF[49] = ['49', 'Currency Code, Transaction',             'F',   3,   'n',    'n',    '0',  'right']
    _DEF[50] = ['50', 'Currency Code, Settlement',              'F',   3,   'n',    'n',    '0',  'right']
    _DEF[51] = ['51', 'Currency Code, Billing',                 'F',   3,   'n',    'n',    '0',  'right']
    _DEF[52] = ['52', 'PIN Data',                               'F',    16, 'b',    'x',    '0',  'right']
    _DEF[53] = ['53', 'Security Related Control Information',   'F',    16, 'n',    'n',    '0',  'right']
    _DEF[54] = ['54', 'Additional Amounts',                   'LLL', 999, 'ans',    'x',    'F',   'left']
    _DEF[55] = ['55', 'ICC Data',                             '0LLL',   999, 'b',   'x',    'F',   'left']
    _DEF[56] = ['56', 'ISO Reserved',                         'LLL', 999, 'ans',    'x',    'F',   'left']
    _DEF[57] = ['57', 'Amount Cash',                            'F',    12, 'n',    'n',    '0',   'right']
    _DEF[58] = ['58', 'Ledger Balance',                         'F',    12, 'n',    'n',    '0',   'right']
    _DEF[59] = ['59', 'Account Balance',                        'F',    12, 'n',    'n',    '0',   'right']
    _DEF[60] = ['60', 'Private Data',                         'LLL',    999, 'ans',    'x',    'F', 'left']
    _DEF[61] = ['61', 'Private Data',                         'LLL',    999, 'ans',    'x',    'F', 'left']
    _DEF[62] = ['62', 'Private Data',                         'LLL',    999, 'ans',    'x',    'F', 'left']
    _DEF[63] = ['63', 'Private Data',                         'LLL',    999, 'ans',    'x',    'F', 'left']
    _DEF[64] = ['64', 'Message Authentication Code',            'F',     16, 'b',       'x',    '0',  'right']
    _DEF[65] = ['65', 'Reserved for ISO Use',                   'F',     64, 'b',       'x',    '0',  'right']
    _DEF[66] = ['66', 'Settlement Code',                        'F',      1, 'n',       'n',    '0',  'right']
    _DEF[67] = ['67', 'Extended Payment Code',                  'F',      2, 'n',       'n',    '0',  'right']
    _DEF[68] = ['68', 'Receiving Institution Country Code',     'F',      3, 'n',       'n',    '0',  'right']
    _DEF[69] = ['69', 'Settlement Institution Country Code',    'F',      3, 'n',       'n',    '0',  'right']
    _DEF[70] = ['70', 'Network Management Information Code',    'F',      3, 'n',       'n',    '0',  'right']
    _DEF[71] = ['71', 'Message Number',                         'F',      4, 'n',       'n',    '0',  'right']
    _DEF[72] = ['72', 'Message Number Last',                    'F',      4, 'n',       'n',    '0',  'right']
    _DEF[73] = ['73', 'Date Action',                            'F',      6, 'n',       'n',    '0',  'right']
    _DEF[74] = ['74', 'Credits, Number',                        'F',     10, 'n',       'n',    '0',  'right']
    _DEF[75] = ['75', 'Credits, Reversal Number',               'F',     10, 'n',       'n',    '0',  'right']
    _DEF[76] = ['76', 'Debits, Number',                         'F',     10, 'n',       'n',    '0',  'right']
    _DEF[77] = ['77', 'Debits, Reversal Number',                'F',     10, 'n',       'n',    '0',  'right']
    _DEF[78] = ['78', 'Transfer, Number',                       'F',     10, 'n',       'n',    '0',  'right']
    _DEF[79] = ['79', 'Transfer, Reversal Number',              'F',     10, 'n',       'n',    '0',  'right']
    _DEF[80] = ['80', 'Inquiries, Number',                      'F',     10, 'n',       'n',    '0',  'right']
    _DEF[81] = ['81', 'Authorizations, Number',                 'F',     10, 'n',       'n',    '0',  'right']
    _DEF[82] = ['82', 'Credits, Processing Fee Amount',         'F',     12, 'n',       'n',    '0',  'right']
    _DEF[83] = ['83', 'Credits, Transaction Fee Amount',        'F',     12, 'n',       'n',    '0',  'right']
    _DEF[84] = ['84', 'Debits, Processing Fee Amount',          'F',     12, 'n',       'n',    '0',  'right']
    _DEF[85] = ['85', 'Debits, Transaction Fee Amount',         'F',     12, 'n',       'n',    '0',  'right']
    _DEF[86] = ['86', 'Credits, Amount',                        'F',     16, 'n',       'n',    '0',  'right']
    _DEF[87] = ['87', 'Credits, Reversal Amount',               'F',     16, 'n',       'n',    '0',  'right']
    _DEF[88] = ['88', 'Debits, Amount',                         'F',     16, 'n',       'n',    '0',  'right']
    _DEF[89] = ['89', 'Debits, Reversal Amount',                'F',     16, 'n',       'n',    '0',  'right']
    _DEF[90] = ['90', 'Original Data Elements',                 'F',     42, 'n',       'n',    '0',  'right']
    _DEF[91] = ['91', 'File Update Code',                       'F',     1, 'an',       'x',    '0',  'right']
    _DEF[92] = ['92', 'File Security Code',                     'F',     2, 'an',       'x',    '0',  'right']
    _DEF[93] = ['93', 'Response Indicator',                     'F',     5, 'an',       'x',    '0',  'right']
    _DEF[94] = ['94', 'Service Indicator',                      'F',     7, 'an',       'x',    '0',  'right']
    _DEF[95] = ['95', 'Replacement Amounts',                    'F',     42,'an',       'x',    '0',  'right']
    _DEF[96] = ['96', 'Message Security Code',                  'F',     64, 'b',       'x',    '0',  'right']
    _DEF[97] = ['97', 'Amount, Net Settlement',                 'F',      16, 'xn',    'c',   '0',  'right']
    _DEF[98] = ['98', 'Payee'                                  'LL',     25, 'ans',      'x',   'F', 'left']
    _DEF[99] = ['99', 'Settlement Institution ID Code',         'LL',       11, 'n',       'n', 'F', 'left']
    _DEF[100] = ['100', 'Receiving Institution ID Code',        'LL',       11, 'n',       'n', 'F', 'left']
    _DEF[101] = ['101', 'File Name',                            'LL',      17,  'ans',     'x', 'F', 'left']
    _DEF[102] = ['102', 'Account Identification 1',             'LL',      28,  'ans',     'x', 'F', 'left']
    _DEF[103] = ['103', 'Account Identification 2',             'LL',      28,  'ans',     'x', 'F', 'left']
    _DEF[104] = ['104', 'Transaction Description',             'LLL',     100,  'ans',     'x', 'F', 'left']
    _DEF[105] = ['105', 'Reserved for ISO use',                'LLL',     999,  'ans',     'x', 'F', 'left']
    _DEF[106] = ['106', 'Reserved for ISO use',                'LLL',     999,  'ans',     'x', 'F', 'left']
    _DEF[107] = ['107', 'Reserved for ISO use',                'LLL',     999,  'ans',     'x', 'F', 'left']
    _DEF[108] = ['108', 'Reserved for ISO use',                'LLL',     999,  'ans',     'x', 'F', 'left']
    _DEF[109] = ['109', 'Reserved for ISO use',                'LLL',     999,  'ans',     'x', 'F', 'left']
    _DEF[110] = ['110', 'Reserved for ISO use',                'LLL',     999,  'ans',     'x', 'F', 'left']
    _DEF[111] = ['111', 'Reserved for ISO use',                'LLL',     999,  'ans',     'x', 'F', 'left']
    _DEF[112] = ['112', 'Key Management Data',                 '0LLL',    999,    'b',     'x', 'F', 'left']
    _DEF[113] = ['113', 'Reserved for National use',           'LLL',     999,  'ans',     'x', 'F', 'left']
    _DEF[114] = ['114', 'Reserved for National use',           'LLL',     999,  'ans',     'x', 'F', 'left']
    _DEF[115] = ['115', 'Reserved for National use',           'LLL',     999,  'ans',     'x', 'F', 'left']
    _DEF[116] = ['116', 'Reserved for National use',           'LLL',     999,  'ans',     'x', 'F', 'left']
    _DEF[117] = ['117', 'Card Status Update Code',               'F',         2,  'ans',   'x', '0',  'right']
    _DEF[118] = ['118', 'Cash Total Number',                    '0LLL',      10, 'n',       'n',  'F', 'left']
    _DEF[119] = ['119', 'Cash Total Amount',                    '0LLL',      10, 'n',       'n',  'F', 'left']
    _DEF[120] = ['120',  'Reserved for Private Use',            'LLL',      999, 'ans',     'x', 'F', 'left']
    _DEF[121] = ['121',  'Reserved for Private Use',            'LLL',      999, 'ans',     'x', 'F', 'left']
    _DEF[122] = ['122',  'Reserved for Private Use',            'LLL',      999, 'ans',     'x', 'F', 'left']
    _DEF[123] = ['123',  'Reserved for Private Use',            'LLL',      999, 'ans',     'x', 'F', 'left']
    _DEF[124] = ['124',  'Reserved for Private Use',            'LLL',      999, 'ans',     'x', 'F', 'left']
    _DEF[125] = ['125',  'Reserved for Private Use',            'LLL',      999, 'ans',     'x', 'F', 'left']
    _DEF[126] = ['126',  'Reserved for Private Use',            'LLL',      999, 'ans',     'x', 'F', 'left']
    _DEF[127] = ['127',  'Reserved for Private Use',            'LLL',      999, 'ans',     'x', 'F', 'left']
    _DEF[128] = ['128',  'MAC Extended',                           'F',       16, 'b',       'x', '0',  'right']


    def __init__(self, iso="", debug=False):
        """Default Constructor of AS2805 Package.
        It initialize a "brand new" AS2805 package
        Example: To Enable debug you can use:
        pack = AS2895(debug=True)
        @param: iso a String that represents the ASCII of the package. The same that you need to pass to setIsoContent() method.
        @param: debug (True or False) default False -> Used to print some debug infos. Only use if want that messages!
        """
        #Bitmap internal representation
        self.BITMAP = []

        #Values
        self._VALUES = []

        #Bitmap ASCII representantion
        self.BITMAP_HEX = ''

        # MTI
        self.MESSAGE_TYPE_INDICATION = ''
        #Debug ?
        self.DEBUG = debug

        self.__initializeBitmap()
        self.__initializeValues()

        if iso != "":
            self.setIsoContent(iso)

    ################################################################################################

    def getLengthType(self, bit):
        """Method that return the bit Type
        @param: bit -> Bit that will be searched and whose type will be returned
        @return: str that represents the type of the bit
        """
        return self._DEF[bit][2]

    ################################################################################################

    def getMaxLength(self, bit):
        """Method that return the bit limit (Max size)
        @param: bit -> Bit that will be searched and whose limit will be returned
        @return: int that indicate the limit of the bit
        """
        return self._DEF[bit][3]

    ################################################################################################

    def getDataType(self, bit):
        """Method that return the bit value type
        @param: bit -> Bit that will be searched and whose value type will be returned
        @return: str that indicate the valuye type of the bit
        """
        return self._DEF[bit][4]


    ################################################################################################


    def getDataFormat(self, bit):
        return self._DEF[bit][5]

    ################################################################################################
    def getAllighnment(self, bit):
        return self._DEF[bit][7]

    ################################################################################################
    def getPadValue(self, bit):
        return self._DEF[bit][6]

    ################################################################################################

    def getBitName(self, bit):
        """Method that return the large bit name
        @param: bit -> Bit that will be searched and whose name will be returned
        @return: str that represents the name of the bit
        """
        return self._DEF[bit][1]

    ################################################################################################

    def setTransationType(self, type):
        """Method that set Transation Type (MTI)
        @param: type -> MTI to be setted
        """

        self.MESSAGE_TYPE_INDICATION = ("0000%s" % type)[-4:]

    ################################################################################################

    def setMTI(self, type):
        """Method that set Transation Type (MTI)
        In fact, is an alias to "setTransationType" method
        @param: type -> MTI to be setted
        """
        self.setTransationType(type)

    ################################################################################################

    def __initializeBitmap(self):
        """Method that inicialize/reset a internal bitmap representation
        It's a internal method, so don't call!
        """

        if self.DEBUG == True:
            print 'Init bitmap'

        if len(self.BITMAP) == 16:
            for cont in range(0, 16):
                self.BITMAP[cont] = self._EMPTY_VALUE
        else:
            for cont in range(0, 16):
                self.BITMAP.append(self._EMPTY_VALUE)


                ################################################################################################

    def __initializeValues(self):
        """Method that inicialize/reset a internal array used to save bits and values
        It's a internal method, so don't call!
        """
        if self.DEBUG == True:
            print 'Init bitmap_values'

        if len(self._VALUES) == 129:
            for cont in range(0, 129):
                self._VALUES[cont] = self._EMPTY_VALUE
        else:
            for cont in range(0, 129):
                self._VALUES.append(self._EMPTY_VALUE)


                ################################################################################################

    def setBit(self, bit, value):
        """Method used to set a bit with a value.
        It's one of the most important method to use when using this library
        @param: bit -> bit number that want to be setted
        @param: value -> the value of the bit
        @return: True/False default True -> To be used in the future!
        @raise: BitInexistent Exception, ValueToLarge Exception
        """
        if bit < 1 or bit > 129:
            raise BitInexistent("Bit number %s dosen't exist!" % bit)

        if self.DEBUG == True:
            print 'Setting Bit %s (%s) = [%s]' % (bit, self.getBitName(bit), ReadableAscii(value))


        if self.getLengthType(bit) == 'F':
            self.__setBitFixedLength(bit, value)
        elif self.getLengthType(bit) == 'LL':
            self.__setBitVariableLength(bit, value, 2)
        elif self.getLengthType(bit) == 'LLL':
            self.__setBitVariableLength(bit, value, 3)
        elif self.getLengthType(bit) == '0LLL':
            self.__setBitVariableLength(bit, value, 4)


        #Continuation bit?
        if bit > 64:
            self.BITMAP[0] = self.BITMAP[0] | self._TMP[2] # need to set bit 1 of first "bit" in bitmap

        if (bit % 8) == 0:
            pos = (bit / 8) - 1
        else:
            pos = (bit / 8)

        #need to check if the value can be there .. AN , N ... etc ... and the size

        self.BITMAP[pos] = self.BITMAP[pos] | self._TMP[(bit % 8) + 1]

        return True

        ################################################################################################

    def showBitmap(self):
        """Method that print the bitmap in ASCII form
        Hint: Try to use getBitmap method and format your own print :)
        """

        self.__buildBitmap()

        # printing
        print self.BITMAP_HEX

    ################################################################################################

    def __buildBitmap(self):
        """Method that build the bitmap ASCII
        It's a internal method, so don't call!
        """

        self.BITMAP_HEX = ''
        self.BITMAP_BIN = ''

        for c in range(0, 16):
            if (self.BITMAP[0] & self._BIT_POSITION_1) != self._BIT_POSITION_1:
            # Only has the first bitmap
            #				if self.DEBUG == True:
            #					print '%d Bitmap = %d(Decimal) = %s (hexa) ' %(c, self.BITMAP[c], hex(self.BITMAP[c]))

                tm = hex(self.BITMAP[c])[2:]
                if len(tm) != 2:
                    tm = '0' + tm
                self.BITMAP_HEX += tm
                self.BITMAP_BIN += chr(self.BITMAP[c])
                if c == 7:
                    break
            else: # second bitmap
            #				if self.DEBUG == True:
            #					print '%d Bitmap = %d(Decimal) = %s (hexa) ' %(c, self.BITMAP[c], hex(self.BITMAP[c]))

                tm = hex(self.BITMAP[c])[2:]
                if len(tm) != 2:
                    tm = '0' + tm
                self.BITMAP_HEX += tm
                self.BITMAP_BIN += chr(self.BITMAP[c])


    ################################################################################################

    def __getBitmapFromStr(self, bitmap):
            """Method that receive a bitmap str and transfor it to ISO8583 object readable.
            @param: bitmap -> bitmap str to be readable
            It's a internal method, so don't call!
            """
            #Need to check if the size is correct etc...
            cont = 0

            if self.BITMAP_HEX != '':
                    self.BITMAP_HEX = ''

            for x in range(0,32,2):
                    if (int(bitmap[0:2],16) & self._BIT_POSITION_1) != self._BIT_POSITION_1: # Only 1 bitmap
                            if self.DEBUG == True:
                                    print 'Token[%d] %s converted to int is = %s' %(x, bitmap[x:x+2], int(bitmap[x:x+2],16))

                            self.BITMAP_HEX += bitmap[x:x+2]
                            self.BITMAP[cont] = int(bitmap[x:x+2],16)
                            if x == 14:
                                    break
                    else: # Second bitmap
                            if self.DEBUG == True:
                                    print 'Token[%d] %s converted to int is = %s' %(x, bitmap[x:x+2], int(bitmap[x:x+2],16))

                            self.BITMAP_HEX += bitmap[x:x+2]
                            self.BITMAP[cont] = int(bitmap[x:x+2],16)
                    cont += 1


    ################################################################################################

    def showBitsFromBitmapStr(self, bitmap):
        """Method that receive a bitmap str, process it, and print a array with bits this bitmap string represents.
        Usualy is used to debug things.
        @param: bitmap -> bitmap str to be analized and translated to "bits"
        """
        bits = self.__initializeBitsFromBitmapStr(bitmap)
        print 'Bits inside %s  = %s' % (bitmap, bits)

    ################################################################################################

    def __initializeBitsFromBitmapStr(self, bitmap):
        """Method that receive a bitmap str, process it, and prepare AS2805 object to understand and "see" the bits and values inside the ISO ASCII package.
        It's a internal method, so don't call!
        @param: bitmap -> bitmap str to be analized and translated to "bits"
        """
        bits = []
        for c in range(0, 16):
            for d in range(1, 9):
                #if self.DEBUG == True:
                #print 'Value (%d)-> %s & %s = %s' % (d,self.BITMAP[c] , self._TMP[d], (self.BITMAP[c] & self._TMP[d]) )
                if (self.BITMAP[c] & self._TMP[d]) == self._TMP[d]:
                    if d == 1: #  e o 8 bit
                        if self.DEBUG == True:
                            print 'Bit %s is present !!!' % ((c + 1) * 8)
                        bits.append((c + 1) * 8)
                        self._VALUES[(c + 1) * 8] = 'X'
                    else:
                        if (c == 0) & (d == 2): # Continuation bit
                            if self.DEBUG == True:
                                print 'Bit 1 is present !!!'

                            bits.append(1)

                        else:
                            if self.DEBUG == True:
                                print 'Bit %s is present !!!' % (c * 8 + d - 1)

                            bits.append(c * 8 + d - 1)
                            self._VALUES[c * 8 + d - 1] = 'X'

        bits.sort()

        return bits

    ################################################################################################

    def __getBitsFromBitmap(self):
        """Method that process the bitmap and return a array with the bits presents inside it.
        It's a internal method, so don't call!
        """
        bits = []
        for c in range(0, 16):
            for d in range(1, 9):
            #				if self.DEBUG == True:
            #					print 'Value (%d)-> %s & %s = %s' % (d,self.BITMAP[c] , self._TMP[d], (self.BITMAP[c] & self._TMP[d]) )
                if (self.BITMAP[c] & self._TMP[d]) == self._TMP[d]:
                    if d == 1: #  e o 8 bit
                        if self.DEBUG == True:
                            print 'Bit %s is present !!!' % ((c + 1) * 8)

                        bits.append((c + 1) * 8)
                    else:
                        if (c == 0) & (d == 2): # Continuation bit
                            if self.DEBUG == True:
                                print 'Bit 1 is present !!!'

                            bits.append(1)

                        else:
                            if self.DEBUG == True:
                                print 'Bit %s is present !!!' % (c * 8 + d - 1)

                            bits.append(c * 8 + d - 1)

        bits.sort()

        return bits

    ################################################################################################

    def __setBitVariableLength(self, bit, value, length):
        """Method that set a bit with value in form LL
        It put the size in front of the value
        Example: pack.setBit(99,'123') -> Bit 99 is a LL type, so this bit, in ASCII form need to be 03123. To understand, 03 is the size of the information and 123 is the information/value
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueToLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > 10 ** length - 1:
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getLengthType(bit), self.getMaxLength(bit)))

        if len(value) > self.getMaxLength(bit):
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.getLengthType(bit), self.getMaxLength(bit)))



        padding = self.getPadValue(bit)
        type = self.getDataType(bit)
        alignment = self.getAllighnment(bit)
        size = "%s" % len(value)

        if type == 'an' or type == 'ans':
            value = binascii.hexlify(value)
        if type == 'b':
            size = str(int(size) / 2)



        #Variable string in need of padding
        if int(size)%2 != 0:
            if alignment == 'left':
                 value = value + padding
            elif alignment == 'right':
                value = padding + value

        if (type == 'an' or type == 'ans' or type == 'b') and self.getLengthType(bit) != '0LLL':

            size = binascii.hexlify(size.zfill(length))

        if self.getLengthType(bit) == '0LLL':
            size = str(int(size) / 2)


        self._VALUES[bit] = "%s%s" % (size.zfill(length), value)
        #print "Setting Bits: " + self._VALUES[bit] + " type: " + type + " Variable"




    def __setBitFixedLength(self, bit, value):
        """Method that set a bit with value in form N
        It complete the size of the bit with a default value
        Example: pack.setBit(3,'30000') -> Bit 3 is a N type, so this bit, in ASCII form need to has size = 6 (ISO especification) so the value 30000 size = 5 need to receive more "1" number.
            In this case, will be "0" in the left. In the package, the bit will be sent like '030000'
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueToLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value



        #if len(value) > self.getMaxLength(bit):
            #value = value[0:self.getMaxLength(bit)]
            #raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (bit, self.getLengthType(bit), self.getMaxLength(bit)))




        length = self.getMaxLength(bit)
        type = self.getDataType(bit)
        format = self.getDataFormat(bit)
        padding = self.getPadValue(bit)
        alignment = self.getAllighnment(bit)

        if type == 'an' or type == 'ans':

            size = "%s" % len(value)
            #if int(size)%2 != 0:
            #    size = int(size) + 1
            if alignment == 'left':
                value = value.ljust(int(size), padding)
            elif alignment == 'right':
                value = value.rjust(int(size), padding)
            value = binascii.hexlify(value)
        size = "%s" % len(value)

        if type == 'b':
            size = "%s" % length
            if int(size)%2 != 0:
                size = int(size) + 1
            if alignment == 'left':
                value = value.ljust(int(size), padding)
            elif alignment == 'right':
                value = value.rjust(int(size), padding)

        size = "%s" % len(value)


        if type == 'xn':#xn type
            number_type = binascii.hexlify(value[0:1])
            value = number_type + value[1:]




        #String string in need of padding
        if int(size)%2 != 0:
            size = int(size) + 1
        if alignment == 'left':
            value = value.ljust(int(size), padding)
        elif alignment == 'right':
            value = value.rjust(int(size), padding)

        self._VALUES[bit] = value
        #print "Setting Bits: " + self._VALUES[bit] + " type: " + type + " Fixed"



    ################################################################################################

    def dumpFields(self):
        """Method that show in detail a list of bits , values and types inside the object
        Example: output to
            (...)
            iso.setBit(2,2)
            iso.setBit(4,4)
            (...)
            iso.showIsoBits()
            (...)
            Bit[2] of type LL has limit 19 = 012
            Bit[4] of type N has limit 12 = 000000000004
            (...)
        """
        res = '\n%s:\n' % self.MESSAGE_TYPE_INDICATION

        for bit in range(0, 129):
            if self._VALUES[bit] <> self._EMPTY_VALUE:
                res += '  '
                if self.getLengthType(bit) == 'LL':
                    res += "[LL     "
                elif self.getLengthType(bit) == 'LLL':
                    res += "[LLL    "
                elif self.getLengthType(bit) == '0LLL':
                    res += "[0LLL   "
                else:
                    res += "[Fixed  "
                res += self.getDataType(bit)
                res += " " * (5 - len(self.getDataType(bit)))
                res += "%6d] " % self.getMaxLength(bit)
                res += ("%s" % bit)
                #PCI-DSS Masking of card holder data
                if bit == 2:    # PAN
                    res += " [%s] " % ReadableAscii(self.getBit(bit))
                else:
                    res += " [%s] " % ReadableAscii(self.getBit(bit))
                res += self.getBitName(bit)
                res += '\n'

                #print res

        return res

        ################################################################################################

    def showRawIso(self):
        """Method that print AS2805 ASCII complete representation
        Example:
        iso = AS2805()
        iso.setMTI('0800')
        iso.setBit(2,2)
        iso.setBit(4,4)
        iso.setBit(12,12)
        iso.setBit(17,17)
        iso.setBit(99,99)
        iso.showRawIso()
        output (print) -> 0800d010800000000000000000002000000001200000000000400001200170299
        Hint: Try to use getRawIso method and format your own print :)
        """

        resp = self.getRawIso()
        print resp

    ################################################################################################

    def getRawIso(self):
        """Method that return AS2805 ASCII complete representation
        Example:
        iso = AS2805()
        iso.setMTI('0800')
        iso.setBit(2,2)
        iso.setBit(4,4)
        iso.setBit(12,12)
        iso.setBit(17,17)
        iso.setBit(99,99)
        str = iso.getRawIso()
        print 'This is the ASCII package %s' % str
        output (print) -> This is the ASCII package 0800d010800000000000000000002000000001200000000000400001200170299

        @return: str with complete ASCII AS2805
        @raise: InvalidMTI Exception
        """

        self.__buildBitmap()

        if self.MESSAGE_TYPE_INDICATION == '':
            raise InvalidMTI('Check MTI! Do you set it?')

        resp = ""

        resp += self.MESSAGE_TYPE_INDICATION
        resp += binascii.hexlify(self.BITMAP_BIN)

        for cont in range(0, 129):
            if self._VALUES[cont] <> self._EMPTY_VALUE:
                resp = "%s%s" % (resp, self._VALUES[cont])

        return resp

    ################################################################################################


    def __setMTIFromStr(self, iso):
        """Method that get the first 4 characters to be the MTI.
         It's a internal method, so don't call!
         """
        if self.DEBUG == True:
            print '__setMTIFromStr(%s)' % ReadableAscii(iso)

        self.MESSAGE_TYPE_INDICATION = iso[0:4]

        if self.DEBUG == True:
            print 'MTI found was [%s]' % self.MESSAGE_TYPE_INDICATION

            ################################################################################################

    def getMTI(self):
        """Method that return the MTI of the package
        @return: str -> with the MTI
        """

        #Need to validate if the MTI was setted ...etc ...
        return self.MESSAGE_TYPE_INDICATION

    ################################################################################################

    def getBitmap(self):
        """Method that return the ASCII Bitmap of the package
        @return: str -> with the ASCII Bitmap
        """
        if self.BITMAP_HEX == '':
            self.__buildBitmap()

        return self.BITMAP_HEX

    ################################################################################################

    def getValuesArray(self):
        """Method that return an internal array of the package
        @return: array -> with all bits, presents or not in the bitmap
        """
        return self._VALUES

    ################################################################################################

    def __getBitFromStr(self, strWithoutMtiBitmap):
        """Method that receive a string (ASCII) without MTI and Bitmaps (first and second), understand it and remove the bits values
        @param: str -> with all bits presents whithout MTI and bitmap
        It's a internal method, so don't call!
        """

        if self.DEBUG == True:
            print '__getBitFromStr(%s)' % ReadableAscii(strWithoutMtiBitmap)

        offset = 0
        # jump bit 1 because it was alread defined in the "__initializeBitsFromBitmapStr"
        for cont in range(2, 129):
            if self._VALUES[cont] <> self._EMPTY_VALUE:
                if self.DEBUG == True:
                    print 'String = %s offset = %s bit = %s' % (strWithoutMtiBitmap[offset:], offset, cont)

                lengthIndicator = 0

                if self.getLengthType(cont) == 'LL':
                    lengthIndicator = 2
                elif self.getLengthType(cont) == 'LLL':
                    lengthIndicator = 3
                elif self.getLengthType(cont) == '0LLL':
                    lengthIndicator = 4



                if lengthIndicator >= 2 and lengthIndicator <= 4 :


                    if self.getDataType(cont) == 'an' or self.getDataType(cont) == 'ans':
                        lengthIndicator *= 2
                        valueSize = int(strWithoutMtiBitmap[offset:offset + lengthIndicator].decode('hex'))
                        valueSize = valueSize * 2


                    elif self.getDataType(cont) == 'b':

                        if self.getLengthType(cont) == '0LLL':

                            valueSize = int(strWithoutMtiBitmap[offset:offset + lengthIndicator])
                        else:
                            lengthIndicator *= 2
                            valueSize = int(strWithoutMtiBitmap[offset:offset + lengthIndicator].decode('hex'))
                            valueSize = valueSize*2

                    elif self.getDataType(cont) == 'n':
                        valueSize = int(strWithoutMtiBitmap[offset:offset + lengthIndicator])


                    else:
                        valueSize = int(strWithoutMtiBitmap[offset:offset + lengthIndicator])


                    if self.DEBUG == True:
                        print 'Variable Length Field (%s) Size = [%s]' % ('L' * lengthIndicator, valueSize)

                    if valueSize > self.getMaxLength(cont):
                        raise ValueToLarge("This bit is larger than the specification!")

                    if valueSize%2 != 0:
                        valueSize += 1

                    self._VALUES[cont] = strWithoutMtiBitmap[offset:offset + lengthIndicator] + strWithoutMtiBitmap[offset + lengthIndicator:offset + lengthIndicator + valueSize]

                    if self.DEBUG == True:
                        print '\tSetting bit [%s] Value=[%s]' % (cont, self._VALUES[cont])


                    offset += valueSize + lengthIndicator



                elif self.getLengthType(cont) == 'F':

                    length = self.getMaxLength(cont)
                    if length % 2 != 0:
                        length += 1


                    if self.getDataType(cont) == 'an' or self.getDataType(cont) == 'ans' :
                        length *= 2
                        self._VALUES[cont] = strWithoutMtiBitmap[offset:length + offset]
                        offset += length
                    else:
                        #print "Offset: " +  strWithoutMtiBitmap[offset:]
                        self._VALUES[cont] = strWithoutMtiBitmap[offset:length + offset]
                        offset += length


                    if self.DEBUG == True:
                        print 'Fixed Length Field Size = [%s]' % (length)
                        print '\tSetting bit [%s] Value=[%s]' % (cont, self._VALUES[cont])


                    ################################################################################################

    def setIsoContent(self, iso):

        if len(iso) < 20:
            raise InvalidAS2805('This is not a valid iso!!')
        if self.DEBUG == True:
            print 'ASCII to process <%s>' % iso

        self.__setMTIFromStr(iso)
        isoT = iso[4:]
        self.__getBitmapFromStr(isoT)
        self.__initializeBitsFromBitmapStr(self.BITMAP_HEX)
        if self.DEBUG == True:
            print 'This is the array of bits (before) %s ' % self._VALUES

        self.__getBitFromStr(iso[4+len(self.BITMAP_HEX):])
        if self.DEBUG == True:
            print 'This is the array of bits (after) %s ' % self._VALUES

            ################################################################################################

    def getBitsAndValues(self):
        """Method that return an array of bits, values, types etc.
			Each array value is a dictionary with: {'bit':X ,'type': Y, 'value': Z} Where:
				bit: is the bit number
				type: is the bit type
				value: is the bit value inside this object
			so the Generic array returned is:  [ (...),{'bit':X,'type': Y, 'value': Z}, (...)]

		Example:
			p1 = AS2805()
			p1.setMTI('0800')
			p1.setBit(2,2)
			p1.setBit(4,4)
			p1.setBit(12,12)
			p1.setBit(17,17)
			p1.setBit(99,99)

			v1 = p1.getBitsAndValues()
			for v in v1:
				print 'Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value'])

		@return: array of values.
        """
        ret = []
        for cont in range(2, 126):
            if self._VALUES[cont] != self._EMPTY_VALUE:
                _TMP = {}
                _TMP['bit'] = "%d" % cont
                _TMP['type'] = self.getLengthType(cont)
                _TMP['value'] = self.getBit(cont)
                ret.append(_TMP)
        return ret

    ################################################################################################

    def getBit(self, bit):
        """Return the value of the bit
		@param: bit -> the number of the bit that you want the value
		@raise: BitInexistent Exception, BitNotSet Exception
        """

        if bit < 1 or bit > 128:
            raise BitInexistent("Bit number %s dosen't exist!" % bit)

        if self._VALUES[bit] == self._EMPTY_VALUE:
            raise BitNotSet("Bit number %s was not set!" % bit)

        if self.getLengthType(bit) == "LL" and (self.getDataType(bit) == 'n' or self.getDataType(bit) == 'z'):
            value = self._VALUES[bit][2:]
        elif self.getLengthType(bit) == "LLL" and (self.getDataType(bit) == 'n' or self.getDataType(bit) == 'z'):
            value = self._VALUES[bit][3:]
        elif self.getLengthType(bit) == "LL" and (self.getDataType(bit) == 'an' or self.getDataType(bit) == 'ans'):
            value = binascii.unhexlify(self._VALUES[bit][4:])
        elif self.getLengthType(bit) == "LLL" and (self.getDataType(bit) == 'an' or self.getDataType(bit) == 'ans' or self.getDataType(bit) == 'b'):
            value = binascii.unhexlify(self._VALUES[bit][6:])
        elif self.getLengthType(bit) == "0LLL" :
            value = self._VALUES[bit][4:]

        else:
            if self.getDataType(bit) == 'an' or self.getDataType(bit) == 'ans':
                value = binascii.unhexlify(self._VALUES[bit])
            else:
                value = self._VALUES[bit]

        return value

    ################################################################################################

    def getNetworkISO(self, bigEndian=True):
        """Method that return AS2805 ASCII package with the size in the beginning
		By default, it return the package with size represented with big-endian.
		Is the same that:
			import struct
			(...)
			iso = AS2805()
			iso.setBit(3,'300000')
			(...)
			ascii = iso.getRawIso()
			# Example: big-endian
			# To little-endian, replace '!h' with '<h'
			netIso = struct.pack('!h',len(iso))
			netIso += ascii
			# Example: big-endian
			# To little-endian, replace 'iso.getNetworkISO()' with 'iso.getNetworkISO(False)'
			print 'This <%s> the same that <%s>' % (iso.getNetworkISO(),netIso)

		@param: bigEndian (True|False) -> if you want that the size be represented in this way.
		@return: size + ASCII AS2805 package ready to go to the network!
		@raise: InvalidMTI Exception
        """

        netIso = ""
        asciiIso = HexToByte(self.getRawIso())

        if bigEndian:
            netIso = struct.pack('!I', len(asciiIso))
            if self.DEBUG == True:
                print 'Pack Big-endian'
        else:
            netIso = struct.pack('<I', len(asciiIso))
            if self.DEBUG == True:
                print 'Pack Little-endian'

        netIso += asciiIso

        return netIso

    ################################################################################################

    """
    determine if the given string is hex
    """
    def __isStringHex(self, s):
        return all(c in string.hexdigits for c in s)

    ################################################################################################
    def setNetworkISO(self, iso, bigEndian=True):

        if len(iso) < 24:
            raise InvalidAS2805('This is not a valid iso!!Invalid Size')

        size = iso[0:2]
        if bigEndian:
            size = struct.unpack('!H', size)
            if self.DEBUG == True:
                print 'Unpack Big-endian'
        else:
            size = struct.unpack('<H', size)
            if self.DEBUG == True:
                print 'Unpack Little-endian'

        #if len(iso) != (size[0] + 2):
        #    raise InvalidAS2805('This is not a valid iso!!The AS2805 ASCII(%s) is less than the size %s!' % (len(iso[2:]), size[0]))

        self.setIsoContent(ByteToHex(iso)[8:])

################################################################################################


def ReadableAscii(s):
    """
    Print readable ascii string, non-readable characters are printed as periods (.)
    """
    r = ''
    for c in s:
        if ord(c) >= 32 and ord(c) <= 126:
            r += c
        else:
            r += '.'
    return r

################################################################################################


def BinaryDump(s):
    """
    Returns a hexdump in postilion trace format. It also removes the leading tcp length indicator

    0000(0000)  30 32 31 30 F2 3E 44 94  2F E0 84 20 00 00 00 00   0210.>D./.. ....
    0016(0010)  04 00 00 22 31 36 2A 2A  2A 2A 2A 2A 2A 2A 2A 2A   ..."16**********
    0032(0020)  2A 2A 2A 2A 2A 2A 30 31  31 30 30 30 30 30 30 30   ******0110000000
    0048(0030)  30 30 30 35 30 30 30 30  31 30 30 34 30 36 34 30   0005000010040640
    ...
    0576(0240)  36 3C 2F 44 61 74 61 3E  3C 2F 52 65 74 72 69 65   6</Data></Retrie
    0592(0250)  76 61 6C 52 65 66 4E 72  3E 3C 2F 42 61 73 65 32   valRefNr></Base2
    0608(0260)  34 44 61 74 61 3E								  4Data>
    """
    #Remove TCP length indicator
    s = s[2:]
    while s != '':
        part = s[:16]
        s = s[16:]

################################################################################################

if __name__ == '__main__':
    iso = AS2805(debug=False)
    iso.setMTI('0420')
    #Set a Fixed Length Field
    iso.setBit(3, '011000')
    iso.setBit(4, '000000002000')
    iso.setBit(7, '0107235144')
    iso.setBit(11, '000518')
    iso.setBit(12, '105144')
    iso.setBit(13, '0108')
    iso.setBit(15, '0108')
    iso.setBit(18, '6011')
    iso.setBit(22, '051')
    iso.setBit(23, '000')
    iso.setBit(25, '41')
    iso.setBit(28, 'D00000200')
    iso.setBit(32, '560258')
    #iso.setBit(33, '61100016')
    iso.setBit(35, '5188680100002932D15122015076719950000')
    iso.setBit(37, '500810510518')
    #iso.setBit(39, '00')
    iso.setBit(41, 'S9218163')
    iso.setBit(42, 'TYME            ')
    iso.setBit(43, '800 LANGDON ST,          MADISON      AU')
    iso.setBit(47, 'TCC01\\EFC00000000\\CCI0\FBKV\\')
    iso.setBit(48, '61E29E04896786B3950552E9118A655D0CD054BF3DC1E35E829C704030DBC8F6')
    iso.setBit(52, 'A8FB4E47EACB0FA1')
    iso.setBit(53, '0000000000000002')
    iso.setBit(55, '9F02060000000020009F03060000000000009F1A020036950500000000005F2A0200369A031501089C01019F37044DFF3952820200009F360200069F3303E0E0809F2701809F2608433B5FDBBC5847FA5F3401009F34030103029F350122')
    iso.setBit(57, '000000000000')
    #iso.setBit(70, '301')
    iso.setBit(64, '29365A0400000000')
   # iso.setBit(99, '1234567')
   # iso.setBit(100, '579944')
   # iso.setBit(128, '027980E700000000')


    print iso.dumpFields()
#    v1 = iso.getBitsAndValues()
#    for v in v1:
#        print 'Bit %s of type %s with value = %s' % (v['bit'], v['type'], v['value'])
    message = iso.getNetworkISO()

    print "getNetworkISO message = [%s]" % (message)
    print "getNetworkISO HEX message = [%s]" % (ByteToHex(message))


    iso_in = AS2805(debug=True)
    iso_in.setNetworkISO(message)

    print iso_in.getBit(48).encode('hex')
    print iso_in.getBit(47)
    print iso_in.dumpFields()


