require 'csv'
require 'active_support/all'

DATA_PATH = 'tmp/out/*.csv'
TIMESLICE_EVENT_KEYS = ["mins", "minsec", "player_id", "secs", "competition", "kickoff", "match_id"]

def parse
	data = Hash.new { |hash, key| hash[key] = [] }
	Dir[DATA_PATH].each do |file_path|
		data_type = file_path.split('/').last.split('.').first
		CSV.foreach(file_path, headers: true) do |row|
			row_data = row.to_hash
			if row_data['minsec']
				data['timeslice_events'] << (TIMESLICE_EVENT_KEYS.map {|key| [key, row_data.delete(key)]}.to_h.merge('data' => row_data, 'data_type' => data_type))
			else
				data[data_type] << row_data
			end
		end
	end

	data['players'] = data['players'].map {|d| [d['id'], d]}.to_h
	data['teams'] = data['teams'].map {|d| [d['id'], d]}.to_h
	# keys = Hash.new { |hash, key| hash[key] = [] }
	# data['timeslice_events'].each do |d|
	# 	keys[d['data_type']] = d['data'].keys
	# end
	# puts keys.to_json
end


parse
