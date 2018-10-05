from mroylib.config import Config


class Worker:

	def recieve(self, *args, **kargs):
		pass

	def report(self, *args, **kargs):
		# return to leader
		pass


class Leader(Worker):

	def __init__(self, conf):
		self._conf = conf

	def summary(self):
		pass

	def dispatch(self, workers):
		pass
