class PlainText(object):
	
	'''
	Plaintext contains the un-encrypted text
	'''

	def __init__(self, text):
		self.plaintext = text


class CipherText(object):

	'''
	CipherText contains a tuple 
	(a,b) = (r*B,r*x*B)
	'''

	def __init__(self, tuple):
		self.a = tuple[0]
		self.b = tuple[1]
		self.pok = tuple[2]

	def getCipher(self):
		return [self.a, self.b,self.pok]

	def __str__(self):
		return "Cipher text: ({:d},{:d}) , ({:d},{:d}) ".format(self.a.x, self.a.y,self.b.x,self.b.y)