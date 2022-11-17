from MyAnimeListAPI import GetAnimeList
from MyAnimeListAPI.ChartingTypes import StackedBarChart

layers = ["None", "1*", "2*", "3*", "4*", "5*", "6*", "7*", "8*", "9*", "10*"]
chart = StackedBarChart("Genre", "Count by Score", layers, title = "Genres by Score")

detailedList = GetAnimeList.GetDetailed("mattyboyh2003")
detailedList = [anime for anime in detailedList if anime["list_status"]["status"] == "completed" ]

chart.SetColours({
    "None" : "#c4c4c4", 
    "1*"   : "#ff0000", 
    "2*"   : "#ff5500", 
    "3*"   : "#ffaa00", 
    "4*"   : "#ffff00", 
    "5*"   : "#aaff00", 
    "6*"   : "#55ff00", 
    "7*"   : "#00ff00", 
    "8*"   : "#00f35a", 
    "9*"   : "#00e8ad", 
    "10*"  : "#00ddff"
})

for anime in detailedList:
    animeScore = anime["list_status"]["score"]
    for genre in anime["advanced_info"]["genres"]:
        if genre["name"] not in chart.GetColumnLabels():
            chart.AddColumn(genre["name"])
        
        columnData = chart.GetColumn(genre["name"])
        columnData[animeScore] += 1
        chart.ModifyColumn(genre["name"], columnData)


order = ["total"]
layers = chart.GetLayers()
layers.reverse()
order.extend(layers)

print(order)

chart.Draw(order)
