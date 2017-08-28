import ctypes

lib = ctypes.cdll.LoadLibrary("tests/libfct_bidon.so")


def callback_python():
	print "I am a callback!"

variable_partagee = False

def triple(x):
	print "je vais calculer le triple de ", x
	print "c'est ", 3 * x
	print "mais je ne renvoie rien"
	global variable_partagee
	variable_partagee = True


lib.call_fct_with_thread(ctypes.CFUNCTYPE(None, ctypes.c_int)(triple), ctypes.c_int(4))

while not variable_partagee:
	continue

print "--> fin du test"



