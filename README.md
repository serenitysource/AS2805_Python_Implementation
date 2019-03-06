AS2805_Python_Implementation
============================

This is an implementation of the AS2805 using python

https://arthurvandermerwe.com/2014/07/06/parsing-as25058583-messages/

============================
http://www.vulcanno.com.br/python/ISO8583.ISO8583.html



class ISO8583
    	Main Class to work with ISO8583 packages.
Used to create, change, send, receive, parse or work with ISO8593 Package version 1993.
It's 100% Python :)
Enjoy it!
Thanks to: Vulcanno IT Solutions <http://www.vulcanno.com.br>
Licence: GPL Version 3
More information: http://code.google.com/p/iso8583py/
 
Example:
        from ISO8583.ISO8583 import ISO8583
        from ISO8583.ISOErrors import *
        
        iso = ISO8583()
        try:
                iso.setMTI('0800')
                iso.setBit(2,2)
                iso.setBit(4,4)
                iso.setBit(12,12)
                iso.setBit(21,21)
                iso.setBit(17,17)
                iso.setBit(49,986)
                iso.setBit(99,99)
        except ValueToLarge, e:
                        print ('Value too large :( %s' % e)
        except InvalidMTI, i:
                        print ('This MTI is wrong :( %s' % i)
                        
        print ('The Message Type Indication is = %s' %iso.getMTI()) 
        
        print ('The Bitmap is = %s' %iso.getBitmap()) 
        iso.showIsoBits();
        print ('This is the ISO8583 complete package %s' % iso.getRawIso())
        print ('This is the ISO8583 complete package to sent over the TCPIP network %s' % iso.getNetworkISO())
 
  	Methods defined here:

__cmp__(self, obj2)
    Method that compare two objects in "==", "!=" and other things
    Example:
            p1 = ISO8583()
            p1.setMTI('0800')
            p1.setBit(2,2)
            p1.setBit(4,4)
            p1.setBit(12,12)
            p1.setBit(17,17)
            p1.setBit(99,99)
     
            #get the rawIso and save in the iso variable
            iso = p1.getRawIso()
     
            p2 = ISO8583()
            p2.setIsoContent(iso)
     
            print ('Is equivalent?')
            if p1 == p1:
                    print ('Yes :)')
            else:
                    print ('Noooooooooo :(')
     
    @param: obj2 -> object that will be compared
    @return: <0 if is not equal, 0 if is equal

__init__(self, iso='', debug=False)
    Default Constructor of ISO8583 Package.
    It inicialize a "brand new" ISO8583 package
    Example: To Enable debug you can use:
            pack = ISO8583(debug=True)
    @param: iso a String that represents the ASCII of the package. The same that you need to pass to setIsoContent() method.
    @param: debug (True or False) default False -> Used to print some debug infos. Only use if want that messages!

getBit(self, bit)
    Return the value of the bit
    @param: bit -> the number of the bit that you want the value
    @raise: BitInexistent Exception, BitNotSet Exception

getBitLimit(self, bit)
    Method that return the bit limit (Max size)
    @param: bit -> Bit that will be searched and whose limit will be returned
    @return: int that indicate the limit of the bit

getBitType(self, bit)
    Method that return the bit Type
    @param: bit -> Bit that will be searched and whose type will be returned
    @return: str that represents the type of the bit

getBitValueType(self, bit)
    Method that return the bit value type 
    @param: bit -> Bit that will be searched and whose value type will be returned
    @return: str that indicate the valuye type of the bit

getBitmap(self)
    Method that return the ASCII Bitmap of the package
    @return: str -> with the ASCII Bitmap

getBitsAndValues(self)
    Method that return an array of bits, values, types etc.
            Each array value is a dictionary with: {'bit':X ,'type': Y, 'value': Z} Where:
                    bit: is the bit number
                    type: is the bit type
                    value: is the bit value inside this object
            so the Generic array returned is:  [ (...),{'bit':X,'type': Y, 'value': Z}, (...)] 
            
    Example:
            p1 = ISO8583()
            p1.setMTI('0800')
            p1.setBit(2,2)
            p1.setBit(4,4)
            p1.setBit(12,12)
            p1.setBit(17,17)
            p1.setBit(99,99)
            
            v1 = p1.getBitsAndValues()
            for v in v1:
                    print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
     
    @return: array of values.

getLargeBitName(self, bit)
    Method that return the large bit name
    @param: bit -> Bit that will be searched and whose name will be returned
    @return: str that represents the name of the bit

getMTI(self)
    Method that return the MTI of the package
    @return: str -> with the MTI

getNetworkISO(self, bigEndian=True)
    Method that return ISO8583 ASCII package with the size in the beginning
    By default, it return the package with size represented with big-endian.
    Is the same that:
            import struct
            (...)
            iso = ISO8583()
            iso.setBit(3,'300000')
            (...)
            ascii = iso.getRawIso()
            # Example: big-endian
            # To little-endian, replace '!h' with '<h'
            netIso = struct.pack('!h',len(iso)) 
            netIso += ascii
            # Example: big-endian
            # To little-endian, replace 'iso.getNetworkISO()' with 'iso.getNetworkISO(False)'
            print ('This <%s> the same that <%s>' % (iso.getNetworkISO(),netIso))
     
    @param: bigEndian (True|False) -> if you want that the size be represented in this way. 
    @return: size + ASCII ISO8583 package ready to go to the network!
    @raise: InvalidMTI Exception

getRawIso(self)
    Method that return ISO8583 ASCII complete representation
    Example: 
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(2,2)
    iso.setBit(4,4)
    iso.setBit(12,12)
    iso.setBit(17,17)
    iso.setBit(99,99)
    str = iso.getRawIso()
    print ('This is the ASCII package %s' % str) 
    output (print) -> This is the ASCII package 0800d010800000000000000000002000000001200000000000400001200170299
     
    @return: str with complete ASCII ISO8583
    @raise: InvalidMTI Exception

getValuesArray(self)
    Method that return an internal array of the package
    @return: array -> with all bits, presents or not in the bitmap

redefineBit(self, bit, smallStr, largeStr, bitType, size, valueType)
    Method that redefine a bit structure in global scope! 
    Can be used to personalize ISO8583 structure to another specification (ISO8583 1987 for example!)
    Hint: If you have a lot of "ValueToLarge Exception" maybe the especification that you are using is different of mine. So you will need to use this method :)
    @param: bit -> bit to be redefined
    @param: smallStr -> a small String representantion of the bit, used to build "user friendly prints", example "2" for bit 2
    @param: largeStr -> a large String representantion of the bit, used to build "user friendly prints" and to be used to inform the "main use of the bit", 
            example "Primary account number (PAN)" for bit 2
    @param: bitType -> type the bit, used to build the values, example "LL" for bit 2. Need to be one of (B, N, AN, ANS, LL, LLL)   
    @param: size -> limit size the bit, used to build/complete the values, example "19" for bit 2.  
    @param: valueType -> value type the bit, used to "validate" the values, example "n" for bit 2. This mean that in bit 2 we need to have only numeric values.
            Need to be one of (a, an, n, ansb, b)
    @raise: BitInexistent Exception, InvalidValueType Exception

setBit(self, bit, value)
    Method used to set a bit with a value.
    It's one of the most important method to use when using this library
    @param: bit -> bit number that want to be setted
    @param: value -> the value of the bit
    @return: True/False default True -> To be used in the future!
    @raise: BitInexistent Exception, ValueToLarge Exception

setIsoContent(self, iso)
    Method that receive a complete ISO8583 string (ASCII) understand it and remove the bits values
    Example:
            iso = '0210B238000102C080040000000000000002100000000000001700010814465469421614465701081100301000000N399915444303500019991544986020   Value not allowed009000095492'
            i2 = ISO8583()
            # in this case, we need to redefine a bit because default bit 42 is LL and in this especification is "N"
            # the rest remain, so we use "get" :)
            i2.redefineBit(42, '42', i2.getLargeBitName(42), 'N', i2.getBitLimit(42), i2.getBitValueType(42) )
            i2.setIsoContent(iso2)
            print ('Bitmap = %s' %i2.getBitmap()) 
            print ('MTI = %s' %i2.getMTI() )
     
            print ('This ISO has bits:')
            v3 = i2.getBitsAndValues()
            for v in v3:
                    print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
                    
    @param: str -> complete ISO8583 string
    @raise: InvalidIso8583 Exception

setMTI(self, type)
    Method that set Transation Type (MTI) 
    In fact, is an alias to "setTransationType" method
    @param: type -> MTI to be setted

setNetworkISO(self, iso, bigEndian=True)
    Method that receive sie + ASCII ISO8583 package and transfor it in the ISO8583 object.
    By default, it recieve the package with size represented with big-endian.
    Is the same that:
    import struct
    (...)
    iso = ISO8583()
    iso.setBit(3,'300000')
    (...)
    # Example: big-endian
    # To little-endian, replace 'iso.getNetworkISO()' with 'iso.getNetworkISO(False)'
    netIso = iso.getNetworkISO()
    newIso = ISO8583()
    # Example: big-endian
    # To little-endian, replace 'newIso.setNetworkISO()' with 'newIso.setNetworkISO(False)'
    newIso.setNetworkISO(netIso)
    #Is the same that:
    #size = netIso[0:2]
    ## To little-endian, replace '!h' with '<h'
    #size = struct.unpack('!h',size )
    #newIso.setIsoContent(netIso[2:size])
    arr = newIso.getBitsAndValues()
    for v in arr:
            print ('Bit %s Type %s Value = %s' % (v['bit'],v['type'],v['value']))
     
    @param: iso -> str that represents size + ASCII ISO8583 package
    @param: bigEndian (True|False) -> Codification of the size.
    @raise: InvalidIso8583 Exception

setTransationType(self, type)
    Method that set Transation Type (MTI)
    @param: type -> MTI to be setted
    @raise: ValueToLarge Exception

showBitmap(self)
    Method that print the bitmap in ASCII form
    Hint: Try to use getBitmap method and format your own print :)

showBitsFromBitmapStr(self, bitmap)
    Method that receive a bitmap str, process it, and print a array with bits this bitmap string represents.
    Usualy is used to debug things.
    @param: bitmap -> bitmap str to be analized and translated to "bits"

showIsoBits(self)
    Method that show in detail a list of bits , values and types inside the object
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

showRawIso(self)
    Method that print ISO8583 ASCII complete representation
    Example: 
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(2,2)
    iso.setBit(4,4)
    iso.setBit(12,12)
    iso.setBit(17,17)
    iso.setBit(99,99)
    iso.showRawIso()
    output (print) -> 0800d010800000000000000000002000000001200000000000400001200170299
    Hint: Try to use getRawIso method and format your own print :)
    
    
    
