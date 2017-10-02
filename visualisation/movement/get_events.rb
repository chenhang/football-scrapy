require 'net/http'
require 'json'

for i in (2..300)
  uri = URI.parse("http://stats.nba.com/stats/locations_getmoments/?gameid=0021500177&eventid=#{i}")

  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Get.new(uri.request_uri)

  response = http.request(request)

  if response.code == "200"
    puts i
    File.open("json/#{i}.json","w") do |f|
      f.write(response.body)
    end
  else
    puts "ERROR!!!"
  end
end
