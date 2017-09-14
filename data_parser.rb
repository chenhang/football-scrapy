require 'oj'
require 'csv'
require 'active_support/all'
BASE_KEYS = ["KG", "CM", "Url", "Apps", "Nation", "Player", "Flag", "Position", "id", "Jersey Number"]
REMOVED_KEYS = ['R']
ACCUMULATION_TYPES = ["Every X minute", "Per 90 mins", "Per game", "Total"]
TOURMENTS = ["Bundesliga", "UEFA Europa League", "Premier League", "Serie A", "La Liga", "Ligue 1", "UEFA Champions League"]
EURO_TOURMENTS = ["UEFA Europa League", "UEFA Champions League"]
LEAGUE_TOURMENTS = TOURMENTS - EURO_TOURMENTS
GENERAL_CATEGORIES = ["passing", "offensive", "defensive", "summary"]
TOURMENT_FILE_KEYS = {"Bundesliga"=>"league_data.json",
 "UEFA Europa League"=>"el_data.json",
 "Premier League"=>"league_data.json",
 "Serie A"=>"league_data.json",
 "La Liga"=>"league_data.json",
 "Ligue 1"=>"league_data.json",
 "Eredivisie"=>"league_data.json",
 "Liga NOS"=>"league_data.json",
 "UEFA Champions League"=>"cl_data.json"}

NEGATIVE_KEYS = ['Fouls_Type_Fouls','Possession loss_Type_Dispossessed', 'Possession loss_Type_UnsuccessfulTouches']
ERROR_KEYS = ['Goals_Body Parts_Per game_PenaltyScored', 'Possession loss_Type_Total Dribbles', 'Key passes_Length_AccCr']

SELECT_KEYS = {'defensive_league_data' => [ 'Tackles_Success_TotalTackles','Clearances_Success_Total', 'Interception_Success_Total', 'Blocks_Type_PassesBlocked', 'Blocks_Type_ShotsBlocked', 'Fouls_Type_Fouls'],
                'passing_league_data' => [ 'Passes_Length_AccSP', 'Passes_Length_AccLB',  'Passes_Type_AccCr', 'Key passes_Length_Short', 'Key passes_Length_Long',],
                'control_league_data' => [ 'Dribbles_Success_Successful', 'Fouls_Type_Fouled', 'Aerial_Success_Won','Possession loss_Type_Dispossessed', 'Possession loss_Type_UnsuccessfulTouches'],
                'attack_league_data' => ['Shots_Zones_OutOfBox','Shots_Zones_PenaltyArea', 'Shots_Body Parts_Head', 'Shots_Situations_Counter', 'Shots_Situations_OpenPlay'],
                'league_data' => [ 'Tackles_Success_TotalTackles','Clearances_Success_Total', 'Interception_Success_Total', 'Blocks_Type_PassesBlocked', 'Blocks_Type_ShotsBlocked', 'Fouls_Type_Fouls',
                                'Passes_Length_AccSP', 'Passes_Length_AccLB',  'Passes_Type_AccCr', 'Key passes_Length_Short', 'Key passes_Length_Long',
                                'Dribbles_Success_Successful', 'Fouls_Type_Fouled', 'Aerial_Success_Won','Possession loss_Type_Dispossessed', 'Possession loss_Type_UnsuccessfulTouches',
                                'Shots_Zones_OutOfBox','Shots_Zones_PenaltyArea', 'Shots_Body Parts_Head', 'Shots_Situations_Counter', 'Shots_Situations_OpenPlay']}


def to_player_json(file_name:'data/league_data.json',selected_keys:['Position'])
  data = JSON.parse(File.read(file_name))
  result = {}
  positions = []
  data.each do |player_gid, player_data|
    positions << player_data['Position']
    result[player_gid] = player_data.select {|key| key.in?(selected_keys)}.to_h
  end
  p positions.uniq.sort
  File.open('data/positions.json', 'wb') {|f| f.write result.to_json}
end

def to_summary_json
  data = JSON.parse(File.read('teams_overall.json'))
  result = {headers: [], data: (Hash.new {|h, k| h[k] = []}), bounds: (Hash.new {|h, k| h[k] = {min: 100000, max: -100000}})}
  data.each do |team_name, team_data|
    result[:headers] = team_data['stats'].keys if result[:headers].blank?
    stats = team_data['stats'].merge('NAME': team_name, 'LEAGUE': team_data['league'])
    result[:data]['All Teams'] << stats
    result[:data][team_data['league']] << stats
    team_data['stats'].each do |key, value|
      result[:bounds][key][:max] = [result[:bounds][key][:max], value].max
      result[:bounds][key][:min] = [result[:bounds][key][:min], value].min
    end
  end
  File.open('data/team_summary.json', 'wb') {|f| f.write result.to_json}
end
def to_csv(with_header: false,file_name:'data/league_data.json',selected_keys:SELECT_KEYS,normalize:true)
  data = JSON.parse(File.read(file_name))
  selected_keys.each do |export_file_name, keys|
    json_data = select_keys_from(data:data,keys:keys,normalize:normalize)
    export_file_name ||= file_name.split('/').last.split('.').first
    CSV.open("csv/#{'original_' unless normalize}#{export_file_name}.csv", "wb") do |csv|
      json_data.each do |player_gid, player_data|
        csv << ([player_gid] + player_data.values)
      end
    end
  end
end

def merge_kmeans_results
  types = []
  SELECT_KEYS.each do |file_name, keys|
    results = JSON.parse(File.read("cluster_result/#{file_name}_players.json"))
    data = {}
    CSV.open("csv/#{file_name}.csv", 'r') do |rows|
      rows.each do |row|
        data[row[0]] = row
      end
    end

    CSV.open("csv/original_#{file_name}.csv", 'r') do |rows|
      rows.each do |row|
        row[1..-1].each_with_index do |original_value, index|
          data[row[0]][index + 1] = "#{original_value}(#{data[row[0]][index + 1]})"
        end
      end
    end

    CSV.open("cluster_result/kmeans_#{file_name}.csv", "wb") do |csv|
      data.values.each_with_index do |row, i|
        key = row.shift
        type = results[key]
        if types.size <= i
          types.append("#{file_name.split('_')[0]}_#{type}")
        else
          types[i] = [types[i], "#{file_name.split('_')[0]}_#{type}"].join(',')
        end
        name = key.split('_')[0]
        team = key.split('_')[2]
        season = key.split('_').last
        csv << ([name, team, season, types[i]] + row)
      end
    end
  end
end

def select_keys_from(data:, normalize:true,keys:)
  all_values = Hash.new {|h, k| h[k] = []}
  new_data = Hash.new {|h, k| h[k] = {}}
  data.each do |player_gid, player_data|
    next if player_data['defensive_Mins'].to_f < 2000 or (player_data['Position'].downcase.in? ['keeper', 'goalkeeper', 'gk'])
    keys.each do |key|
      value = (player_data[key] || player_data[key.split('_').insert(2, ACCUMULATION_TYPES[1]).join('_')]).gsub('-','').to_f
      # real_key = player_data[key] ? key : key.split('_').insert(2, ACCUMULATION_TYPES[1]).join('_')
      new_data[player_gid][key] = value
      all_values[key] << value
    end
  end
  if normalize
    range_values = Hash.new {|h, k| h[k] = []}
    all_values.each do |key, value|
      range_values[key] << value.min
      range_values[key] << value.max
    end
    new_data.each do |player_gid, player_data|
      range_values.each do |key, value|
        player_data[key] = (player_data[key] - range_values[key].first)/(range_values[key].last - range_values[key].first)
        player_data[key] = 1-player_data[key] if NEGATIVE_KEYS.include?(key)
      end
    end
  end
  return new_data
end

def split_json
  json_data = Oj.load(File.open("team_stats.json"))
  # descriptions = {}
  # all_keys = []
  # data = Hash.new {|h, k| h[k] = Hash.new {|h, k| h[k] = {}} }
  # league_data.keys : ["teams", "id", "name"]
  json_data.each do |league_id, league_data|
    file_name = "json_data/#{league_id}-#{league_data['name']}.jsoni"
    puts "#{file_name} start."
    File.open(file_name, 'wb') do |file|
      file.write(league_data.to_json)
    end
    puts "#{file_name} done."
    # team_data.keys : ["tourments", "characteristic", "id", "name"]
    # league_data['teams'].each do |team_id, team_data|
    #   puts team_data['name']
    # end
  end
end

def combined_json
  descriptions = {}
  all_keys = []
  data = Hash.new {|h, k| h[k] = Hash.new {|hh, kk| hh[kk] = {}} }
  Dir["team_stats/*.json"].reverse.each do |file_name|
    # league_data.keys : ["teams", "id", "name"]
    puts 'Start JSON loading: ' + file_name
    league_data = nil
    league_data = Oj.load(File.read("#{file_name}"))
    puts 'End JSON loading: ' + file_name
    # league_id = file_name.split('/').last.split('.').first
    # team_data.keys : ["tourments", "characteristic", "id", "name"]
    league_data['teams'].each do |team_id, team_data|
      puts team_id
      puts team_data['name']
      # tourment_data.keys : ["detailed", "passing", "offensive", "defensive", "summary"]
      team_data['tourments'].each do |tourment_name, seasons|
        puts tourment_name
        seasons.each do |season, tourment_data|
          puts season
          file_name = TOURMENT_FILE_KEYS[tourment_name]
          GENERAL_CATEGORIES.each do |category|
            category_data = tourment_data[category]
            category_data['stats'].each do |player_id, player_data|
              player_data.each do |key, value|
                next if REMOVED_KEYS.include?(key)
                combined_key = BASE_KEYS.include?(key) ? key : [category, key].join('_')
                simple_key = combined_key
                player_key = [player_data['Player'], player_id, team_data['name'], team_id, season].join('_')
                data[file_name][player_key][combined_key] = value
                data[file_name][player_key].update({'Team Name' => team_data['name'], 'Team ID' => team_id, 'League' => tourment_name, 'Season' => season})
                descriptions[simple_key] ||= category_data['legend'][key]
                all_keys << simple_key
              end
            end
          end
          # detailed_data.keys : ["category", "stats", "sub_category", "accumulation_type"]
          tourment_data['detailed'].each do |detailed_data|
            detailed_data['stats']['stats'].each do |player_id, player_data|
              player_data.each do |key, value|
                next if REMOVED_KEYS.include?(key)
                combined_key = BASE_KEYS.include?(key) ? key : ["category", "sub_category", "accumulation_type"].map {|data_key| detailed_data[data_key] }.append(key).join('_')
                simple_key = BASE_KEYS.include?(key) ? key : ["category", "sub_category"].map {|data_key| detailed_data[data_key] }.append(key).join('_')
                player_key = [player_data['Player'], player_id, team_data['name'], team_id, season].join('_')
                data[file_name][player_key][combined_key] = value
                descriptions[simple_key] ||= detailed_data['stats']['legend'][key]
                all_keys << simple_key
              end
            end
          end
        end
      end
    end
  end
  puts 'Merge data'
  data.each do |file_name, tourment_data|
    tourment_data.each do |player_gid, player_data|
      player_data.keys.select {|k| k.include?('InAcc') }.each do |key|
        # Add Pass Total Keys
        total_key = key.gsub('InAcc', 'Total')
        accumulation_key = ACCUMULATION_TYPES.find {|k| total_key.include?(k)}
        simple_key = key.gsub("_#{accumulation_key}", '')
        player_data[total_key] = [player_data[key], player_data[key.gsub('InAcc', 'Acc')]].map {|v| v.gsub('-','').to_f }.sum.to_s
        simple_total_key = simple_key.gsub('InAcc', 'Total')
        descriptions[simple_total_key] = descriptions[simple_key].to_s.gsub('Inaccurate', 'Total')
        all_keys << simple_total_key
      end
    end
  end

  puts 'Saving all'
  data.each do |file_name, tourment_data|
    puts file_name
    File.open("data/#{file_name}", 'wb') do |file|
      file.write(Oj.dump(tourment_data))
    end
  end

  puts 'Saving by league'
  data['league_data.json'].group_by {|k, v| v['League']}.each do |league_name, league_data|
    puts league_name
    File.open("data/#{league_name}.json", 'wb') do |file|
      file.write(Oj.dump(league_data.to_h))
    end
  end

  puts 'Saving Keys and Desc'
  File.open("data/all_keys.json", 'wb') do |file|
    file.write(all_keys.uniq.to_json)
  end

  File.open("data/descriptions.json", 'wb') do |file|
    file.write(descriptions.to_json)
  end
end

def remove_errors
  team_ids = ["296"]#["255", "8071", "5948", "2187", "2008", "288", "299", "296"]#["1285", "73", "87"]#["3429", "30", "1285", "2889", "779", "75", "267", "278", "73", "80", "87", "54", "65", "67", "69", "145", "1364", "249"]
  data = JSON.parse(File.read('team_stats.json'))
  data.keys.each do |league_id|
    data[league_id]['teams'].except!(*team_ids)
  end
  File.open('team_stats.json', 'wb') do |file|
    file.write(data.to_json)
  end
end

def get_errors
  result = Hash.new {|h,k| h[k] = []}
  error_keys = Hash.new {|h,k| h[k] = []}
  puts 'Start!'
  TOURMENT_FILE_KEYS.values.uniq.each do |file_name|
    puts 'Start: ' + file_name
    has_error = false
    data = Oj.load(File.read("data/#{file_name}"))
    puts 'Loading done: ' + file_name
    keys = data.values.find {|v| (v.keys & ERROR_KEYS).blank? && (v.keys & ["Tackles_Success_Every X minute_DribbledPast"]).any? }.keys
    data.each do |player_id, player_data|
      keys.each do |key|
        unless player_data.has_key?(key)
          has_error = true
          error_keys[file_name] << (player_data.keys - keys)
          result[file_name] << player_id
        end
      end
    end
    puts file_name + ' has error!!!'
    puts 'End: ' + file_name
  end
  p error_keys.values.flatten.uniq
  result.each do |k, v|
    p k, v.uniq.map {|kk| kk.split('_').last(2).join('_') }.uniq
  end
end

def get_error_keys
  error_teams = []
  parser = Yajl::Parser.new
  json_data = parser.parse(File.open("team_stats.json"))
  # league_data.keys : ["teams", "id", "name"]
  json_data.each do |league_id, league_data|
    league_data['teams'].each do |team_id, team_data|
      team_data['tourments'].each do |tourment_name, seasons|
        puts tourment_name
        seasons.each do |season, tourment_data|
          ["passing", "offensive", "defensive", "summary"].each do |key|
            if tourment_data[key]['stats']['www.whoscored.com']
              error_teams << team_id
            end
          end
          if tourment_data['detailed'].any? {|d| d['stats']['stats']['www.whoscored.com'].present? }
            error_teams << team_id
          end
        end
      end
    end
  end
  p error_teams.uniq
end

# combined_json
# get_errors
# remove_errors
to_csv(normalize: true)
to_csv(normalize: false)
# merge_kmeans_results()
# get_error_keys
# to_summary_json
# to_player_json()
