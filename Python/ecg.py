import signal_utilities as su 

#PLAY AROUND WITH MIN_FREQUENCY UNTIL IT WORKS
class ECG(object):
	def __init__(self, sample_frequency = 200, range_ = 0.1, reference_available = False):
		self.sample_frequency = sample_frequency
		self.range_ = range_
		self.reference_available = reference_available
		self.initialization_period = self.sample_frequency * 3

		self.samples_between_beats = su.Basic_Stats(length = 3) #sized two or three, averaged to get BPM
		#self.samples_between_beats.add_data(0)
		self.signal_tracker = su.PkPk(sample_frequency = sample_frequency, min_frequency = self.sample_frequency / 20, max_frequency = self.sample_frequency / 10) #PLAY AROUND WITH MIN_FREQUENCY UNTIL IT WORKS
		self.BPM = 0

		self.data_points_received = 0
		self.initialization_data = su.Basic_Stats(length = self.initialization_period) 
		self.average_pkpk = -1
		self.pkpk_threshold_ratio = 1.5
		self.data_samples_since_beat = 0 
		self.first_beat = True
		#self.just_detected_beat = False #if true, prevents another beat from being detected for 1/2 of last beat-to-beat time

	def initialize(self, data):
		current_pkpk = self.signal_tracker.get_pkpk(data)['pkpk']
		if self.average_pkpk == -1:
			self.average_pkpk = current_pkpk
		else:
			self.average_pkpk = self.initialization_data.get_average(current_pkpk)

	def get_BPM(self, data):
		average_delay = 0
		if self.data_points_received < self.initialization_period:
			self.initialize(data)
			self.data_points_received += 1
		else:
			print "not initializing anymore"
			current_pkpk = self.signal_tracker.get_pkpk(data)['pkpk']
			self.data_samples_since_beat += 1
			if (current_pkpk > self.average_pkpk * self.pkpk_threshold_ratio) and (self.first_beat == True or self.data_samples_since_beat > 0.5 * self.samples_between_beats.data_points[0]):
				#self.just_detected_beat = True
				if self.first_beat == True:
					self.samples_between_beats.add_data(self.data_samples_since_beat)
					self.first_beat = False
				
				average_delay = self.samples_between_beats.get_average(self.data_samples_since_beat) 

				self.data_samples_since_beat = 0
				#beat detected, disable detection for next ... seconds (fraction of time between most recent beat intervals)
				self.BPM = 60.0 * self.sample_frequency / average_delay

		return self.BPM
