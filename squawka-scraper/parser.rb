require 'csv'
require 'active_support/all'
# require 'pycall/import'
# include PyCall::Import
# pyimport 'matplotlib', as: :mp
# mp.rcParams[:backend] = 'TkAgg' if mp.rcParams[:backend] == 'MacOSX'
# pyimport 'matplotlib.pyplot', as: 'plt'

# require "matplotlib"
# Matplotlib.use("Qt5Agg")
# require 'matplotlib/pyplot'

DATA_PATH = 'tmp/out/*.csv'
OUT_PATH = 'tmp/game_data.json'
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
	data['timeslice_events'] = data['timeslice_events'].sort_by {|d| d['minsec'].to_f }
	data['players'] = data['players'].map {|d| [d['id'], d]}.to_h
	data['teams'] = data['teams'].map {|d| [d['id'], d]}.to_h
	# keys = Hash.new { |hash, key| hash[key] = [] }
	# data['timeslice_events'].each do |d|
	# 	keys[d['data_type']] = d['data'].keys
	# end
	# puts keys.to_json
	File.open(OUT_PATH, 'w') {|f| f.write(data.to_json)}
end

def positions
  positions = JSON.parse(File.read('positions.json'))
  results = []
  positions.each do |k, v|
    x, y = k.split(',', -1)
    results << {x_loc: x, y_loc: y, size: v}
  end
  sizes = results.map {|d| d[:size]}
  p sizes.sort
  results.each do |d|
    d[:per] = (d[:size] - sizes.min)/(sizes.max - sizes.min).to_f
  end
  File.open('position_locations.json', 'wb') do |file|
    file.write(results.to_json)
  end
end


positions
